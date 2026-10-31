from datetime import datetime, timedelta

from core.models import ConsumptionPoint
from detection.features import (
    MIN_FLOW_LITERS,
    extract_features,
    hour_baseline_from_history,
)


def _point(start, liters, *, device="meter-a", minutes=5):
    return ConsumptionPoint(
        user_id=8,
        window_started_at=start,
        window_finished_at=start + timedelta(minutes=minutes),
        consumption_liters=liters,
        anomaly_detected=False,
        device_id=device,
    )


def test_continuous_flow_requires_unbroken_positive_windows():
    start = datetime(2026, 10, 31, 3, 10)
    recent = [
        _point(start - timedelta(minutes=10), 1.0),
        _point(start - timedelta(minutes=5), 1.2),
    ]

    result = extract_features(_point(start, 1.5), recent, 0.0, 0.0)

    assert result.consecutive_flow_windows == 3

    broken = [recent[0], _point(start - timedelta(minutes=5), 0.2)]
    result_with_break = extract_features(_point(start, 1.5), broken, 0.0, 0.0)

    assert result_with_break.consecutive_flow_windows == 1
    assert MIN_FLOW_LITERS == 0.2


def test_flow_counter_stops_at_a_time_gap():
    start = datetime(2026, 10, 31, 3, 10)
    prior = _point(start - timedelta(minutes=6), 2.0)

    result = extract_features(_point(start, 2.0), [prior], 0.0, 0.0)

    assert result.consecutive_flow_windows == 1


def test_hour_baseline_uses_only_matching_hour_and_requires_three_samples():
    start = datetime(2026, 10, 31, 3, 0)
    history = [
        _point(start - timedelta(days=3), 2.0),
        _point(start - timedelta(days=2), 4.0),
        _point(start - timedelta(days=1), 6.0),
        _point(start - timedelta(hours=1), 100.0),
    ]

    mean, std = hour_baseline_from_history(3, history)
    short_mean, short_std = hour_baseline_from_history(
        4, [_point(start.replace(hour=4), 1.0), _point(start.replace(hour=4) - timedelta(days=1), 3.0)]
    )

    assert mean == 4.0
    assert std > 0
    assert (short_mean, short_std) == (0.0, 0.0)


def test_feature_extraction_marks_only_hours_before_six_as_overnight():
    midnight = datetime(2026, 10, 31, 0, 0)
    five_am = datetime(2026, 10, 31, 5, 0)
    six_am = datetime(2026, 10, 31, 6, 0)

    assert extract_features(_point(midnight, 1), [], 0, 0).is_overnight == 1
    assert extract_features(_point(five_am, 1), [], 0, 0).is_overnight == 1
    assert extract_features(_point(six_am, 1), [], 0, 0).is_overnight == 0
