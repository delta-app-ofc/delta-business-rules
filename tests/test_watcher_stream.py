from datetime import datetime, timedelta

from detection import baseline, watcher


def _doc(start, liters=1.5, user_id=9):
    return {
        "_id": "current",
        "device_id": "ESP32-1001",
        "user_id": user_id,
        "window_started_at": start,
        "window_finished_at": start + timedelta(minutes=5),
        "consumption_liters": liters,
        "lpm_average": liters / 5,
        "anomaly_detected": False,
    }


class FakeCursor:
    def __init__(self, documents):
        self.documents = list(documents)
        self.sorting = None

    def sort(self, field, direction):
        self.sorting = (field, direction)
        self.documents.sort(
            key=lambda document: document[field],
            reverse=direction < 0,
        )
        return self

    def __iter__(self):
        return iter(self.documents)


class FakeCollection:
    def __init__(self, history=(), events=()):
        self.history = list(history)
        self.events = list(events)
        self.find_calls = []
        self.last_cursor = None
        self.watch_args = None
        self.updates = []
        self.alerts = []

    def find(self, query):
        self.find_calls.append(query)
        self.last_cursor = FakeCursor(self.history)
        return self.last_cursor

    def watch(self, pipeline, *, full_document):
        self.watch_args = (pipeline, full_document)
        return FakeStream(self.events)

    def update_one(self, query, update):
        self.updates.append((query, update))

    def insert_one(self, document):
        self.alerts.append(document)


class FakeStream:
    def __init__(self, events):
        self.events = events

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def __iter__(self):
        return iter(self.events)


class FakeDatabase:
    def __init__(self, telemetry=None, app=None):
        self.consumption_summary = telemetry
        self.alerts_history = app


class FakeClient:
    def __init__(self, telemetry, app):
        self.databases = {
            watcher.MONGO_DB_TELEMETRY: FakeDatabase(telemetry=telemetry),
            watcher.MONGO_DB_APP: FakeDatabase(app=app),
        }

    def __getitem__(self, name):
        return self.databases[name]


def test_fetch_history_filters_same_device_and_orders_by_time():
    current_start = datetime(2026, 10, 31, 14, 0)
    current = _doc(current_start)
    prior = _doc(current_start - timedelta(minutes=5), user_id="9")
    collection = FakeCollection([prior])

    history = watcher._fetch_history(collection, current, hours=2)

    assert collection.find_calls == [
        {
            "device_id": "ESP32-1001",
            "window_started_at": {
                "$gte": current_start - timedelta(hours=2),
                "$lt": current_start,
            },
        }
    ]
    assert collection.last_cursor.sorting == ("window_started_at", 1)
    assert history[0].user_id == 9
    assert history[0].consumption_liters == 1.5


def test_watcher_reads_baseline_before_update_and_records_continuous_alert(monkeypatch):
    start = datetime(2026, 10, 31, 3, 30)
    history = [
        _doc(start - timedelta(minutes=5 * (index + 1)))
        for index in range(5)
    ]
    current = _doc(start)
    telemetry = FakeCollection(history, [{"fullDocument": current}])
    app = FakeCollection()
    client = FakeClient(telemetry, app)
    events = []

    monkeypatch.setattr(watcher, "get_client", lambda: client)
    monkeypatch.setattr(
        watcher, "get_property_classification", lambda user_id: "RESIDENCIAL"
    )
    monkeypatch.setattr(
        baseline,
        "read_baseline",
        lambda user_id, hour: events.append(("read", user_id, hour))
        or (0.5, 0.0, 20),
    )
    monkeypatch.setattr(
        baseline,
        "update_baseline",
        lambda user_id, hour, value: events.append(
            ("baseline_update", user_id, hour, value)
        ),
    )

    watcher.run(z_threshold=3.0)

    assert events == [
        ("read", 9, 3),
        ("baseline_update", 9, 3, 1.5),
    ]
    assert telemetry.watch_args == (
        [{"$match": {"operationType": "insert"}}],
        "updateLookup",
    )
    assert telemetry.updates == [
        ({"_id": "current"}, {"$set": {"anomaly_detected": True}})
    ]
    assert app.alerts == [
        {
            "device_id": "ESP32-1001",
            "user_id": 9,
            "alert_type": "vazamento_continuo",
            "triggered_at": start,
            "resolved_at": None,
            "severity": "medium",
        }
    ]


def test_watcher_updates_anomaly_flag_without_alert_for_isolated_flow(monkeypatch):
    start = datetime(2026, 10, 31, 12, 0)
    current = _doc(start, liters=5.0)
    telemetry = FakeCollection(events=[{"fullDocument": current}])
    app = FakeCollection()
    client = FakeClient(telemetry, app)
    monkeypatch.setattr(watcher, "get_client", lambda: client)
    monkeypatch.setattr(
        watcher, "get_property_classification", lambda user_id: "RESIDENCIAL"
    )
    monkeypatch.setattr(baseline, "read_baseline", lambda user_id, hour: (0.0, 0.0, 0))
    monkeypatch.setattr(baseline, "update_baseline", lambda *args: None)

    watcher.run(z_threshold=3.0)

    assert telemetry.updates == [
        ({"_id": "current"}, {"$set": {"anomaly_detected": False}})
    ]
    assert app.alerts == []
