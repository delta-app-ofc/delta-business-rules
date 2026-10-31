from core import config, db_mongo, db_postgres


class FakeCursor:
    def __init__(self, row=None):
        self.row = row
        self.calls = []
        self.closed = False

    def execute(self, query, parameters=None):
        self.calls.append((query, parameters))

    def fetchone(self):
        return self.row

    def close(self):
        self.closed = True


class FakeConnection:
    def __init__(self, row=None):
        self.fake_cursor = FakeCursor(row)
        self.closed = False

    def cursor(self):
        return self.fake_cursor

    def close(self):
        self.closed = True


def test_get_conn_uses_split_postgres_configuration(monkeypatch):
    calls = []
    monkeypatch.setattr(db_postgres, "HOST_DB", "db.local")
    monkeypatch.setattr(db_postgres, "PORT_DB", "5432")
    monkeypatch.setattr(db_postgres, "USER_DB", "reader")
    monkeypatch.setattr(db_postgres, "PASSWORD_DB", "local-only")
    monkeypatch.setattr(db_postgres, "NAME_DB", "delta")
    monkeypatch.setattr(
        db_postgres.psycopg2,
        "connect",
        lambda **kwargs: calls.append(kwargs) or "connection",
    )

    assert db_postgres.get_conn() == "connection"
    assert calls == [
        {
            "host": "db.local",
            "port": "5432",
            "user": "reader",
            "password": "local-only",
            "dbname": "delta",
        }
    ]


def test_get_conn_falls_back_to_database_url_when_split_values_are_incomplete(monkeypatch):
    calls = []
    monkeypatch.setattr(db_postgres, "HOST_DB", None)
    monkeypatch.setattr(db_postgres, "PORT_DB", None)
    monkeypatch.setattr(db_postgres, "USER_DB", None)
    monkeypatch.setattr(db_postgres, "PASSWORD_DB", None)
    monkeypatch.setattr(db_postgres, "NAME_DB", None)
    monkeypatch.setattr(db_postgres, "DATABASE_URL", "postgresql://unit-test")
    monkeypatch.setattr(
        db_postgres.psycopg2,
        "connect",
        lambda url: calls.append(url) or "connection",
    )

    assert db_postgres.get_conn() == "connection"
    assert calls == ["postgresql://unit-test"]


def test_user_property_lookup_closes_resources_and_returns_integer(monkeypatch):
    connection = FakeConnection(("17",))
    monkeypatch.setattr(db_postgres, "get_conn", lambda: connection)

    result = db_postgres.get_user_property_id(9)

    assert result == 17
    assert connection.fake_cursor.calls[0][1] == (9,)
    assert "ORDER BY id" in connection.fake_cursor.calls[0][0]
    assert connection.fake_cursor.closed is True
    assert connection.closed is True


def test_classification_lookup_skips_second_query_without_property(monkeypatch):
    opened = []
    monkeypatch.setattr(
        db_postgres, "get_user_property_id", lambda user_id: None
    )
    monkeypatch.setattr(
        db_postgres, "get_conn", lambda: opened.append(True)
    )

    assert db_postgres.get_property_classification(9) is None
    assert opened == []


def test_classification_lookup_returns_group_and_closes_connection(monkeypatch):
    connection = FakeConnection(("RESIDENCIAL",))
    monkeypatch.setattr(
        db_postgres, "get_user_property_id", lambda user_id: 17
    )
    monkeypatch.setattr(db_postgres, "get_conn", lambda: connection)

    assert db_postgres.get_property_classification(9) == "RESIDENCIAL"
    assert connection.fake_cursor.calls == [
        ("SELECT fn_get_property_classification_group(%s);", (17,))
    ]
    assert connection.fake_cursor.closed is True
    assert connection.closed is True


def test_config_reports_missing_connections_and_accepts_complete_split_values(monkeypatch):
    monkeypatch.setattr(config, "DATABASE_URL", "")
    monkeypatch.setattr(config, "HOST_DB", "db.local")
    monkeypatch.setattr(config, "PORT_DB", "5432")
    monkeypatch.setattr(config, "USER_DB", "reader")
    monkeypatch.setattr(config, "PASSWORD_DB", "local-only")
    monkeypatch.setattr(config, "NAME_DB", "delta")
    monkeypatch.setattr(config, "MONGODB_URI", "mongodb://localhost")
    assert config.validate_config() == []

    monkeypatch.setattr(config, "PASSWORD_DB", None)
    monkeypatch.setattr(config, "MONGODB_URI", "")
    problems = config.validate_config()
    assert len(problems) == 2
    assert "DATABASE_URL" in problems[0]
    assert problems[1] == "MONGODB_URI ausente no .env."


def test_mongo_client_is_lazy_cached_and_timezone_aware(monkeypatch):
    created = []

    class FakeMongoClient:
        def __init__(self, uri, *, tz_aware):
            created.append((uri, tz_aware))

    db_mongo.get_client.cache_clear()
    monkeypatch.setattr(db_mongo, "MONGODB_URI", "mongodb://unit-test")
    monkeypatch.setattr(db_mongo, "MongoClient", FakeMongoClient)

    try:
        first = db_mongo.get_client()
        second = db_mongo.get_client()
        assert first is second
        assert created == [("mongodb://unit-test", True)]
    finally:
        db_mongo.get_client.cache_clear()
