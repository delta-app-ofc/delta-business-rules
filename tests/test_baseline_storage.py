from datetime import datetime, timezone

import pytest

from detection import baseline


class FakeCollection:
    def __init__(self, document=None):
        self.document = document
        self.indexes = []
        self.updates = []

    def create_index(self, keys, *, unique):
        self.indexes.append((keys, unique))

    def find_one(self, query):
        self.query = query
        return self.document

    def update_one(self, query, update, *, upsert):
        self.updates.append((query, update, upsert))


def test_read_baseline_defaults_to_empty_for_a_new_user_hour(monkeypatch):
    collection = FakeCollection()
    monkeypatch.setattr(baseline, "_collection", lambda: collection)

    assert baseline.read_baseline(5, 3) == (0.0, 0.0, 0)
    assert collection.query == {"user_id": 5, "hour": 3}


def test_read_baseline_converts_saved_values_to_numeric_types(monkeypatch):
    collection = FakeCollection(
        {"mean": "3.5", "variance": "2.25", "sample_count": "8"}
    )
    monkeypatch.setattr(baseline, "_collection", lambda: collection)

    assert baseline.read_baseline(5, 3) == (3.5, 2.25, 8)


def test_update_baseline_uses_upsert_and_utc_timestamp(monkeypatch):
    collection = FakeCollection()
    monkeypatch.setattr(baseline, "_collection", lambda: collection)

    baseline.update_baseline(5, 3, 4.25)

    query, update, upsert = collection.updates[0]
    assert query == {"user_id": 5, "hour": 3}
    assert update["$set"]["mean"] == 4.25
    assert update["$set"]["variance"] == 0.0
    assert update["$set"]["sample_count"] == 1
    assert update["$set"]["updated_at"].tzinfo == timezone.utc
    assert upsert is True


def test_update_baseline_moves_existing_mean_using_ewma(monkeypatch):
    collection = FakeCollection(
        {"mean": 2.0, "variance": 1.0, "sample_count": 10}
    )
    monkeypatch.setattr(baseline, "_collection", lambda: collection)

    baseline.update_baseline(5, 3, 8.0)

    saved = collection.updates[0][1]["$set"]
    expected_mean, expected_variance = baseline.ewma_update(2.0, 1.0, 10, 8.0)
    assert saved["mean"] == expected_mean
    assert saved["variance"] == expected_variance
    assert saved["sample_count"] == 11


def test_baseline_index_is_unique_for_each_user_and_hour(monkeypatch):
    collection = FakeCollection()
    monkeypatch.setattr(baseline, "_collection", lambda: collection)

    baseline.ensure_indexes()

    assert collection.indexes == [([("user_id", 1), ("hour", 1)], True)]
