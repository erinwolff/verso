import datetime as dt

import pytest

from app import storage


def test_write_read_roundtrip(data_dir):
    e = storage.write_entry("2026-06-08", "The rain held off until evening.")
    assert e is not None
    assert e.words == 6
    got = storage.read_entry("2026-06-08")
    assert got is not None
    assert got.body == "The rain held off until evening."
    assert got.words == 6
    assert got.created == got.updated  # first write


def test_update_preserves_created_bumps_updated(data_dir):
    first = storage.write_entry("2026-06-08", "one two three")
    assert first is not None
    second = storage.write_entry("2026-06-08", "one two three four five six")
    assert second is not None
    assert second.created == first.created
    assert second.words == 6
    # updated is monotonic (>= created); identical-second writes are allowed
    assert second.updated >= first.created


def test_empty_body_deletes(data_dir):
    storage.write_entry("2026-06-08", "something")
    assert storage.read_entry("2026-06-08") is not None
    result = storage.write_entry("2026-06-08", "   \n  ")
    assert result is None
    assert storage.read_entry("2026-06-08") is None


def test_invalid_date_rejected(data_dir):
    with pytest.raises(ValueError):
        storage.write_entry("2026-6-8", "bad date")
    with pytest.raises(ValueError):
        storage.write_entry("not-a-date", "nope")


def test_list_dates_newest_first(data_dir):
    storage.write_entry("2026-06-01", "a")
    storage.write_entry("2026-06-08", "b")
    storage.write_entry("2026-06-04", "c")
    assert storage.list_dates() == ["2026-06-08", "2026-06-04", "2026-06-01"]


def test_index_counts(data_dir):
    storage.write_entry("2026-06-01", "one two")
    storage.write_entry("2026-06-02", "three four five")
    idx = storage.get_index()
    assert idx["entries"] == 2
    assert idx["words"] == 5
    assert idx["first"] == "2026-06-01"
    assert idx["last"] == "2026-06-02"


# --- streak (one-day warm-ember grace, §8) --------------------------------

def test_streak_lit_today():
    today = dt.date(2026, 6, 8)
    dates = {dt.date(2026, 6, 6), dt.date(2026, 6, 7), dt.date(2026, 6, 8)}
    s = storage.compute_streak(dates, today)
    assert s == {"count": 3, "state": "lit"}


def test_streak_warm_yesterday():
    today = dt.date(2026, 6, 8)
    dates = {dt.date(2026, 6, 6), dt.date(2026, 6, 7)}  # wrote through yesterday
    s = storage.compute_streak(dates, today)
    assert s == {"count": 2, "state": "warm"}


def test_streak_cold_two_days_gap():
    today = dt.date(2026, 6, 8)
    dates = {dt.date(2026, 6, 5), dt.date(2026, 6, 6)}  # last = 2 days ago
    s = storage.compute_streak(dates, today)
    assert s == {"count": 0, "state": "cold"}


def test_streak_empty():
    assert storage.compute_streak(set(), dt.date(2026, 6, 8)) == {
        "count": 0,
        "state": "cold",
    }


def test_streak_breaks_on_gap_within_run():
    today = dt.date(2026, 6, 8)
    # gap between the 4th and 6th breaks the run; only 7th+8th count
    dates = {dt.date(2026, 6, 4), dt.date(2026, 6, 7), dt.date(2026, 6, 8)}
    s = storage.compute_streak(dates, today)
    assert s == {"count": 2, "state": "lit"}
