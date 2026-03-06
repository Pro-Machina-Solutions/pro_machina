import datetime as dt
import json

import numpy as np
import pytest

from pro_machina import ShiftBreak, ShiftBuilder, ShiftPattern
from pro_machina.durations import Hours, Mins
from pro_machina.exceptions import ShiftDefinitionError, ShiftIntegrityError
from pro_machina.problem.shifts import _ShiftDay

# ===========================================================================
# Helpers / shared fixtures
# ===========================================================================

REF_DATE = "2026-02-02"  # A Monday
REF_DT = dt.datetime(2026, 2, 2)


def make_simple_builder(name: str = "Test Shift") -> ShiftBuilder:
    """Return a builder pre-loaded with a standard Mon–Fri day shift."""
    b = ShiftBuilder(REF_DATE, name)
    # Mon–Fri: 06:00–18:00
    for day in range(5):
        date = REF_DT + dt.timedelta(days=day)
        b.add_work_period(
            start_time=date.replace(hour=6),
            end_time=date.replace(hour=18),
        )
    # Sat & Sun: down days
    b.add_downday(REF_DT + dt.timedelta(days=5))
    b.add_downday(REF_DT + dt.timedelta(days=6))
    return b


def built_simple_builder() -> ShiftBuilder:
    b = make_simple_builder()
    b.build()
    return b


class TestShiftBreak:
    def test_default_productivity_zero(self):
        sb = ShiftBreak(start="2026-02-02 10:00:00", end="2026-02-02 10:30:00")
        assert sb.productivity == 0

    def test_custom_productivity(self):
        sb = ShiftBreak(
            start="2026-02-02 10:00:00",
            end="2026-02-02 10:30:00",
            productivity=50,
        )
        assert sb.productivity == 50


# ===========================================================================
# _ShiftDay
# ===========================================================================


class TestShiftDay:
    """Unit tests for the internal _ShiftDay helper."""

    def _day(self, date: dt.date = dt.date(2026, 2, 2)):
        """Return a fully contiguous _ShiftDay for *date*."""
        midnight_start = dt.datetime(date.year, date.month, date.day, 0, 0, 0)
        midnight_end = midnight_start + dt.timedelta(days=1)
        d = _ShiftDay()
        d.add_period(
            {"start": midnight_start, "end": midnight_end, "prod": 100}
        )
        return d

    # --- validate ---

    def test_validate_passes_for_contiguous_full_day(self):
        self._day().validate()  # should not raise

    def test_validate_raises_when_no_periods(self):
        d = _ShiftDay()
        with pytest.raises(ShiftDefinitionError, match="No hours"):
            d.validate()

    def test_validate_raises_when_not_starting_at_midnight(self):
        d = _ShiftDay()
        d.add_period(
            {
                "start": dt.datetime(2026, 2, 2, 1, 0, 0),
                "end": dt.datetime(2026, 2, 3, 0, 0, 0),
                "prod": 0,
            }
        )
        with pytest.raises(ShiftIntegrityError, match="midnight"):
            d.validate()

    def test_validate_raises_when_not_ending_at_next_midnight(self):
        d = _ShiftDay()
        d.add_period(
            {
                "start": dt.datetime(2026, 2, 2, 0, 0, 0),
                "end": dt.datetime(2026, 2, 2, 23, 0, 0),
                "prod": 0,
            }
        )
        with pytest.raises(ShiftIntegrityError, match="until midnight"):
            d.validate()

    def test_validate_raises_non_contiguous_periods(self):
        d = _ShiftDay()
        d.add_period(
            {
                "start": dt.datetime(2026, 2, 2, 0, 0),
                "end": dt.datetime(2026, 2, 2, 12, 0),
                "prod": 100,
            }
        )
        d.add_period(
            {
                "start": dt.datetime(2026, 2, 2, 13, 0),  # gap!
                "end": dt.datetime(2026, 2, 3, 0, 0),
                "prod": 0,
            }
        )
        with pytest.raises(ShiftIntegrityError, match="Non-contiguous"):
            d.validate()

    # --- for_json / from_json round-trip ---

    def test_for_json_converts_datetimes_to_strings(self):
        d = self._day()
        result = d.for_json()
        for period in result:
            assert isinstance(period["start"], str)
            assert isinstance(period["end"], str)

    def test_from_json_restores_datetimes(self):
        raw = [
            {
                "start": "2026-02-02 00:00:00",
                "end": "2026-02-03 00:00:00",
                "prod": 100,
            }
        ]
        d = _ShiftDay.from_json(raw)
        assert isinstance(d.periods[0]["start"], dt.datetime)
        assert isinstance(d.periods[0]["end"], dt.datetime)

    def test_json_roundtrip(self):
        d = self._day()
        serialised = d.for_json()
        deserialised = _ShiftDay.from_json(serialised)
        assert deserialised.periods[0]["prod"] == d.periods[0]["prod"]


# ===========================================================================
# ShiftBuilder – construction & basic configuration
# ===========================================================================


class TestShiftBuilderInit:
    def test_name_stored(self):
        b = ShiftBuilder(REF_DATE, "MyShift")
        assert b.name == "MyShift"

    def test_ref_date_normalised_to_midnight(self):
        b = ShiftBuilder("2026-02-02 14:30:00", "X")
        assert b.ref_start_date == dt.datetime(2026, 2, 2, 0, 0, 0)

    def test_datetime_object_accepted_as_ref_date(self):
        b = ShiftBuilder(dt.datetime(2026, 2, 2, 8, 0), "X")
        assert b.ref_start_date == dt.datetime(2026, 2, 2, 0, 0, 0)

    def test_initial_state(self):
        b = ShiftBuilder(REF_DATE, "X")
        assert not b._is_built
        assert b._shift_periods == []
        assert b._shift_days == []


# ===========================================================================
# ShiftBuilder – add_work_period
# ===========================================================================


class TestAddWorkPeriod:
    def test_basic_period_added(self):
        b = ShiftBuilder(REF_DATE, "X")
        b.add_work_period("2026-02-02 06:00:00", "2026-02-02 18:00:00")
        assert len(b._shift_periods) == 1

    def test_productivity_defaults_to_100(self):
        b = ShiftBuilder(REF_DATE, "X")
        b.add_work_period("2026-02-02 06:00:00", "2026-02-02 18:00:00")
        assert b._shift_periods[0]["prod"] == 100

    def test_custom_productivity(self):
        b = ShiftBuilder(REF_DATE, "X")
        b.add_work_period(
            "2026-02-02 06:00:00", "2026-02-02 18:00:00", productivity=80
        )
        assert b._shift_periods[0]["prod"] == 80

    def test_productivity_zero_allowed(self):
        b = ShiftBuilder(REF_DATE, "X")
        b.add_work_period(
            "2026-02-02 06:00:00", "2026-02-02 18:00:00", productivity=0
        )
        assert b._shift_periods[0]["prod"] == 0

    def test_productivity_100_allowed(self):
        b = ShiftBuilder(REF_DATE, "X")
        b.add_work_period(
            "2026-02-02 06:00:00", "2026-02-02 18:00:00", productivity=100
        )
        assert b._shift_periods[0]["prod"] == 100

    def test_productivity_below_zero_raises(self):
        b = ShiftBuilder(REF_DATE, "X")
        with pytest.raises(ValueError, match="0-100"):
            b.add_work_period(
                "2026-02-02 06:00:00", "2026-02-02 18:00:00", productivity=-1
            )

    def test_productivity_above_100_raises(self):
        b = ShiftBuilder(REF_DATE, "X")
        with pytest.raises(ValueError, match="0-100"):
            b.add_work_period(
                "2026-02-02 06:00:00", "2026-02-02 18:00:00", productivity=101
            )

    def test_single_shiftbreak_wrapped_in_list(self):
        b = ShiftBuilder(REF_DATE, "X")
        brk = ShiftBreak("2026-02-02 10:00:00", "2026-02-02 10:30:00")
        b.add_work_period(
            "2026-02-02 06:00:00", "2026-02-02 18:00:00", breaks=brk
        )
        assert isinstance(b._shift_periods[0]["breaks"], list)

    def test_list_of_breaks_accepted(self):
        b = ShiftBuilder(REF_DATE, "X")
        breaks = [
            ShiftBreak("2026-02-02 10:00:00", "2026-02-02 10:30:00"),
            ShiftBreak("2026-02-02 13:00:00", "2026-02-02 13:30:00"),
        ]
        b.add_work_period(
            "2026-02-02 06:00:00", "2026-02-02 18:00:00", breaks=breaks
        )
        assert len(b._shift_periods[0]["breaks"]) == 2

    def test_invalid_break_type_raises(self):
        b = ShiftBuilder(REF_DATE, "X")
        with pytest.raises(TypeError):
            b.add_work_period(
                "2026-02-02 06:00:00",
                "2026-02-02 18:00:00",
                breaks=["not a ShiftBreak"],
            )

    def test_break_productivity_below_zero_raises(self):
        b = ShiftBuilder(REF_DATE, "X")
        brk = ShiftBreak(
            "2026-02-02 10:00:00", "2026-02-02 10:30:00", productivity=-1
        )
        with pytest.raises(ValueError, match="0-100"):
            b.add_work_period(
                "2026-02-02 06:00:00", "2026-02-02 18:00:00", breaks=brk
            )

    def test_break_productivity_above_100_raises(self):
        b = ShiftBuilder(REF_DATE, "X")
        brk = ShiftBreak(
            "2026-02-02 10:00:00", "2026-02-02 10:30:00", productivity=101
        )
        with pytest.raises(ValueError, match="0-100"):
            b.add_work_period(
                "2026-02-02 06:00:00", "2026-02-02 18:00:00", breaks=brk
            )

    def test_cannot_add_after_build(self):
        b = built_simple_builder()
        with pytest.raises(ValueError, match="finalised"):
            b.add_work_period("2026-02-09 06:00:00", "2026-02-09 18:00:00")

    def test_no_breaks_defaults_to_empty_list(self):
        b = ShiftBuilder(REF_DATE, "X")
        b.add_work_period("2026-02-02 06:00:00", "2026-02-02 18:00:00")
        assert b._shift_periods[0]["breaks"] == []


# ===========================================================================
# ShiftBuilder – add_downday
# ===========================================================================


class TestAddDownday:
    def test_downday_recorded(self):
        b = ShiftBuilder(REF_DATE, "X")
        b.add_downday("2026-02-02")
        assert len(b._shift_periods) == 1
        assert b._shift_periods[0]["is_down_day"] is True

    def test_downday_date_parsed(self):
        b = ShiftBuilder(REF_DATE, "X")
        b.add_downday(dt.datetime(2026, 2, 2))
        assert isinstance(b._shift_periods[0]["start"], dt.datetime)

    def test_downday_collision_with_activity_earlier(self):
        b = ShiftBuilder(REF_DATE, "X")
        b.add_work_period("2026-02-02 22:00:00", "2026-02-03 00:00:01")
        with pytest.raises(ShiftDefinitionError, match="activity defined"):
            b.add_downday("2026-02-03")

    def test_cannot_add_downday_after_build(self):
        b = built_simple_builder()
        with pytest.raises(ValueError, match="finalised"):
            b.add_downday("2026-02-09")


# ===========================================================================
# ShiftBuilder – build() happy paths
# ===========================================================================


class TestBuildHappyPath:
    def test_build_sets_is_built(self):
        b = make_simple_builder()
        b.build()
        assert b._is_built

    def test_build_creates_7_shift_days(self):
        b = make_simple_builder()
        b.build()
        assert len(b._shift_days) == 7

    def test_shift_days_are_contiguous(self):
        b = built_simple_builder()
        for i in range(len(b._shift_days) - 1):
            assert (
                b._shift_days[i].periods[-1]["end"]
                == b._shift_days[i + 1].periods[0]["start"]
            )

    def test_all_days_start_at_midnight(self):
        b = built_simple_builder()
        for day in b._shift_days:
            start = day.periods[0]["start"]
            assert start == dt.datetime(
                start.year, start.month, start.day, 0, 0, 0
            )

    def test_all_days_end_at_next_midnight(self):
        b = built_simple_builder()
        for day in b._shift_days:
            end = day.periods[-1]["end"]
            assert end == dt.datetime(end.year, end.month, end.day, 0, 0, 0)

    def test_downday_is_all_zero_prod(self):
        b = built_simple_builder()
        # days 5 and 6 (index) are the down days
        for day in b._shift_days[5:]:
            for period in day.periods:
                assert period["prod"] == 0

    def test_work_day_has_prod_periods(self):
        b = built_simple_builder()
        # Monday (index 0) should contain a prod=100 period
        prods = {p["prod"] for p in b._shift_days[0].periods}
        assert 100 in prods

    def test_build_twice_raises(self):
        b = make_simple_builder()
        b.build()
        with pytest.raises(ValueError, match="already been finalised"):
            b.build()

    def test_periods_sorted_by_start_before_processing(self):
        """Periods added out of order should still build correctly."""
        b = ShiftBuilder(REF_DATE, "Sorted")
        # Add Wednesday first, then Monday–Tuesday, then rest
        b.add_work_period("2026-02-04 06:00:00", "2026-02-04 18:00:00")
        b.add_work_period("2026-02-02 06:00:00", "2026-02-02 18:00:00")
        b.add_work_period("2026-02-03 06:00:00", "2026-02-03 18:00:00")
        b.add_work_period("2026-02-05 06:00:00", "2026-02-05 18:00:00")
        b.add_work_period("2026-02-06 06:00:00", "2026-02-06 18:00:00")
        b.add_downday("2026-02-07")
        b.add_downday("2026-02-08")
        b.build()  # should not raise
        assert b._is_built

    def test_full_day_shift_midnight_to_midnight(self):
        """A single 24-hour period should build cleanly."""
        b = ShiftBuilder(REF_DATE, "24h")
        b.add_work_period("2026-02-02 00:00:00", "2026-02-03 00:00:00")
        b.build()
        assert b._is_built

    def test_multiple_periods_same_day(self):
        """Two separate work windows on the same day (morning + afternoon)."""
        b = ShiftBuilder(REF_DATE, "Split")
        b.add_work_period("2026-02-02 06:00:00", "2026-02-02 12:00:00")
        b.add_work_period("2026-02-02 13:00:00", "2026-02-02 18:00:00")
        for i in range(1, 6):
            b.add_downday(REF_DT + dt.timedelta(days=i))
        b.build()
        assert b._is_built

    def test_overnight_shift(self):
        """Shift starting Monday evening, ending Tuesday morning."""
        b = ShiftBuilder(REF_DATE, "Overnight")
        b.add_work_period("2026-02-02 22:00:00", "2026-02-03 06:00:00")
        for i in range(2, 6):
            b.add_downday(REF_DT + dt.timedelta(days=i))
        b.build()
        assert b._is_built

    def test_shift_with_single_break(self):
        b = ShiftBuilder(REF_DATE, "BreakShift")
        brk = ShiftBreak("2026-02-02 10:00:00", "2026-02-02 10:30:00")
        b.add_work_period(
            "2026-02-02 06:00:00", "2026-02-02 18:00:00", breaks=brk
        )
        for i in range(1, 7):
            b.add_downday(REF_DT + dt.timedelta(days=i))
        b.build()
        assert b._is_built

    def test_shift_with_two_breaks(self):
        b = ShiftBuilder(REF_DATE, "TwoBreaks")
        breaks = [
            ShiftBreak("2026-02-02 10:00:00", "2026-02-02 10:30:00"),
            ShiftBreak("2026-02-02 13:00:00", "2026-02-02 13:30:00"),
        ]
        b.add_work_period(
            "2026-02-02 06:00:00", "2026-02-02 18:00:00", breaks=breaks
        )
        for i in range(1, 7):
            b.add_downday(REF_DT + dt.timedelta(days=i))
        b.build()
        assert b._is_built

    def test_break_with_reduced_productivity(self):
        b = ShiftBuilder(REF_DATE, "PartialBreak")
        brk = ShiftBreak(
            "2026-02-02 10:00:00", "2026-02-02 10:30:00", productivity=50
        )
        b.add_work_period(
            "2026-02-02 06:00:00", "2026-02-02 18:00:00", breaks=brk
        )
        for i in range(1, 7):
            b.add_downday(REF_DT + dt.timedelta(days=i))
        b.build()
        # Check that the break's prod=50 appears in the shift day periods
        prods = [p["prod"] for p in b._shift_days[0].periods]
        assert 50 in prods

    def test_break_spanning_midnight(self):
        """Break that starts late Mon and ends early Tue."""
        b = ShiftBuilder(REF_DATE, "MidnightBreak")
        brk = ShiftBreak("2026-02-02 23:00:00", "2026-02-03 01:00:00")
        b.add_work_period(
            "2026-02-02 20:00:00", "2026-02-03 06:00:00", breaks=brk
        )
        for i in range(2, 6):
            b.add_downday(REF_DT + dt.timedelta(days=i))
        b.build()
        assert b._is_built

    def test_all_downdays(self):
        """A pattern with all downdays (e.g., planned shutdown week)."""
        b = ShiftBuilder(REF_DATE, "AllDown")
        for i in range(7):
            b.add_downday(REF_DT + dt.timedelta(days=i))
        b.build()
        assert b._is_built
        for day in b._shift_days:
            for period in day.periods:
                assert period["prod"] == 0


# ===========================================================================
# ShiftBuilder – build() error paths
# ===========================================================================


class TestBuildErrorPaths:
    def test_first_period_not_on_ref_date_raises(self):
        b = ShiftBuilder(REF_DATE, "X")
        b.add_work_period("2026-02-03 06:00:00", "2026-02-03 18:00:00")
        with pytest.raises(ShiftDefinitionError, match="reference start date"):
            b.build()

    def test_gap_in_pattern_raises(self):
        """A missing day within the pattern should raise."""
        b = ShiftBuilder(REF_DATE, "X")
        b.add_work_period("2026-02-02 06:00:00", "2026-02-02 18:00:00")
        # Skip Tuesday entirely, jump straight to Wednesday
        b.add_work_period("2026-02-04 06:00:00", "2026-02-04 18:00:00")
        b.add_downday("2026-02-05")
        b.add_downday("2026-02-06")
        b.add_downday("2026-02-07")
        b.add_downday("2026-02-08")
        with pytest.raises(ShiftDefinitionError, match="missing"):
            b.build()

    def test_period_end_before_start_raises(self):
        b = ShiftBuilder(REF_DATE, "X")
        b.add_work_period("2026-02-02 18:00:00", "2026-02-02 06:00:00")
        for i in range(1, 7):
            b.add_downday(REF_DT + dt.timedelta(days=i))
        with pytest.raises(ShiftDefinitionError):
            b.build()

    def test_period_spanning_more_than_24h_raises(self):
        b = ShiftBuilder(REF_DATE, "X")
        b.add_work_period("2026-02-02 06:00:00", "2026-02-04 06:00:00")
        with pytest.raises(ShiftDefinitionError):
            b.build()

    def test_break_outside_work_period_raises(self):
        b = ShiftBuilder(REF_DATE, "X")
        brk = ShiftBreak("2026-02-02 18:30:00", "2026-02-02 19:00:00")
        b.add_work_period(
            "2026-02-02 06:00:00", "2026-02-02 18:00:00", breaks=brk
        )
        for i in range(1, 7):
            b.add_downday(REF_DT + dt.timedelta(days=i))
        with pytest.raises(ShiftDefinitionError, match="contained"):
            b.build()

    def test_break_end_before_start_raises(self):
        b = ShiftBuilder(REF_DATE, "X")
        brk = ShiftBreak("2026-02-02 10:30:00", "2026-02-02 10:00:00")
        b.add_work_period(
            "2026-02-02 06:00:00", "2026-02-02 18:00:00", breaks=brk
        )
        for i in range(1, 7):
            b.add_downday(REF_DT + dt.timedelta(days=i))
        with pytest.raises(ShiftDefinitionError):
            b.build()

    def test_overlapping_breaks_raise(self):
        b = ShiftBuilder(REF_DATE, "X")
        breaks = [
            ShiftBreak("2026-02-02 10:00:00", "2026-02-02 10:45:00"),
            ShiftBreak(
                "2026-02-02 10:30:00", "2026-02-02 11:00:00"
            ),  # overlaps
        ]
        b.add_work_period(
            "2026-02-02 06:00:00", "2026-02-02 18:00:00", breaks=breaks
        )
        for i in range(1, 7):
            b.add_downday(REF_DT + dt.timedelta(days=i))
        with pytest.raises(ShiftDefinitionError, match="overlapping"):
            b.build()

    def test_empty_pattern_raises(self):
        """Building with no periods at all should raise."""
        b = ShiftBuilder(REF_DATE, "Empty")
        with pytest.raises((ShiftDefinitionError, IndexError, Exception)):
            b.build()


# ===========================================================================
# ShiftBuilder – save_pattern / load_pattern
# ===========================================================================


class TestSaveLoadPattern:
    def test_save_creates_file(self, tmp_path):
        b = built_simple_builder()
        fp = tmp_path / "shift.json"
        b.save_pattern(fp)
        assert fp.exists()

    def test_save_produces_valid_json(self, tmp_path):
        b = built_simple_builder()
        fp = tmp_path / "shift.json"
        b.save_pattern(fp)
        with open(fp) as f:
            data = json.load(f)
        assert "name" in data
        assert "ref_start_date" in data
        assert "data" in data
        assert "created" in data

    def test_save_name_preserved(self, tmp_path):
        b = built_simple_builder()
        fp = tmp_path / "shift.json"
        b.save_pattern(fp)
        with open(fp) as f:
            data = json.load(f)
        assert data["name"] == b.name

    def test_save_ref_date_preserved(self, tmp_path):
        b = built_simple_builder()
        fp = tmp_path / "shift.json"
        b.save_pattern(fp)
        with open(fp) as f:
            data = json.load(f)
        assert data["ref_start_date"] == "2026-02-02"

    def test_save_raises_if_not_built(self, tmp_path):
        b = make_simple_builder()
        fp = tmp_path / "shift.json"
        with pytest.raises(ValueError, match="not been finalised"):
            b.save_pattern(fp)

    def test_load_round_trip(self, tmp_path):
        b = built_simple_builder()
        fp = tmp_path / "shift.json"
        b.save_pattern(fp)
        loaded = ShiftBuilder._load_pattern(fp)
        assert loaded.name == b.name
        assert loaded._is_built
        assert len(loaded._shift_days) == len(b._shift_days)

    def test_load_validates_pattern(self, tmp_path):
        """Corrupt the JSON so the loaded pattern fails validation."""
        b = built_simple_builder()
        fp = tmp_path / "shift.json"
        b.save_pattern(fp)

        with open(fp) as f:
            data = json.load(f)

        # Remove a day to break contiguity
        data["data"].pop(2)
        with open(fp, "w") as f:
            json.dump(data, f)

        with pytest.raises(
            (ShiftIntegrityError, ShiftDefinitionError, IndexError, Exception)
        ):
            ShiftBuilder._load_pattern(fp)

    def test_loaded_shift_days_are_contiguous(self, tmp_path):
        b = built_simple_builder()
        fp = tmp_path / "shift.json"
        b.save_pattern(fp)
        loaded = ShiftBuilder._load_pattern(fp)
        for i in range(len(loaded._shift_days) - 1):
            assert (
                loaded._shift_days[i].periods[-1]["end"]
                == loaded._shift_days[i + 1].periods[0]["start"]
            )

    def test_data_count_preserved_after_round_trip(self, tmp_path):
        b = built_simple_builder()
        original_day_count = len(b._shift_days)
        fp = tmp_path / "shift.json"
        b.save_pattern(fp)
        loaded = ShiftBuilder._load_pattern(fp)
        assert len(loaded._shift_days) == original_day_count


# ===========================================================================
# ShiftPattern
# ===========================================================================


class TestShiftPattern:
    def test_instantiation_from_built_builder(self):
        b = built_simple_builder()
        sp = ShiftPattern(b)
        assert sp.name == b.name

    def test_raises_if_builder_not_built(self):
        b = make_simple_builder()
        with pytest.raises(ValueError, match="not been finalised"):
            ShiftPattern(b)

    def test_name_attribute(self):
        b = built_simple_builder()
        sp = ShiftPattern(b)
        assert sp.name == "Test Shift"

    def test_builder_reference_stored(self):
        b = built_simple_builder()
        sp = ShiftPattern(b)
        assert sp._builder is b

    def test_load_from_file(self, tmp_path):
        b = built_simple_builder()
        fp = tmp_path / "shift.json"
        b.save_pattern(fp)
        sp = ShiftPattern.load_from_file(fp)
        assert isinstance(sp, ShiftPattern)

    def test_load_from_file_name(self, tmp_path):
        b = built_simple_builder()
        fp = tmp_path / "shift.json"
        b.save_pattern(fp)
        sp = ShiftPattern.load_from_file(fp)
        assert sp.name == b.name

    def test_load_from_file_is_built(self, tmp_path):
        b = built_simple_builder()
        fp = tmp_path / "shift.json"
        b.save_pattern(fp)
        sp = ShiftPattern.load_from_file(fp)
        assert sp._builder._is_built


class TestShiftPatternYieldDay:
    @pytest.fixture
    def pattern(self):
        return ShiftPattern(built_simple_builder())

    def test_returns_ndarray(self, pattern):
        result = pattern._yield_day("2026-02-02", Hours(1))
        assert isinstance(result, np.ndarray)

    def test_array_length_matches_timestep_hourly(self, pattern):
        result = pattern._yield_day("2026-02-02", Hours(1))
        assert len(result) == 24

    def test_array_length_matches_timestep_30min(self, pattern):
        result = pattern._yield_day("2026-02-02", Mins(30))
        assert len(result) == 48

    def test_working_day_has_nonzero_productivity(self, pattern):
        result = pattern._yield_day("2026-02-02", Hours(1))
        assert result.sum() > 0

    def test_down_day_all_zeros(self, pattern):
        result = pattern._yield_day("2026-02-07", Hours(1))
        assert np.all(result == 0)

    def test_production_hours_correct(self, pattern):
        """06:00–18:00 = 12 hours at 100%, rest zero"""
        result = pattern._yield_day("2026-02-02", Hours(1))
        assert result[8:18].sum() == 1000.0  # 8 * 100
        assert result[:6].sum() == 0
        assert result[18:].sum() == 0

    def test_cyclical_pattern_repeats(self, pattern):
        """Day 8 (next Monday) should be identical to day 1"""
        week1 = pattern._yield_day("2026-02-02", Hours(1))
        week2 = pattern._yield_day("2026-02-09", Hours(1))
        np.testing.assert_array_equal(week1, week2)

    def test_date_before_base_raises(self, pattern):
        with pytest.raises(ValueError, match="before the reference date"):
            pattern._yield_day("2025-01-01", Hours(1))

    def test_non_divisible_timestep_raises(self, pattern):
        with pytest.raises(ValueError, match="not cleanly divisible"):
            pattern._yield_day("2026-02-02", Mins(7))

    def test_yield_day_with_break(self):
        b = ShiftBuilder(REF_DATE, "break_test")
        lunch = ShiftBreak("2026-02-02 12:00:00", "2026-02-02 13:00:00")
        b.add_work_period(
            "2026-02-02 08:00:00",
            "2026-02-02 16:00:00",
            breaks=lunch,
        )
        b.build()
        p = ShiftPattern(b)
        result = p._yield_day("2026-02-02", Hours(1))
        # Lunch hour should be 0
        assert result[12] == 0
        # Normal working hours should be 100
        assert result[8] == 100
        assert result[15] == 100

    def test_reduced_productivity_break_reflected(self):
        b = ShiftBuilder(REF_DATE, "half_break")
        half = ShiftBreak(
            "2026-02-02 12:00:00", "2026-02-02 13:00:00", productivity=50
        )
        b.add_work_period(
            "2026-02-02 08:00:00",
            "2026-02-02 16:00:00",
            breaks=half,
        )
        b.build()
        p = ShiftPattern(b)
        result = p._yield_day("2026-02-02", Hours(1))
        assert result[12] == 50

    def test_multiple_activities_in_bucket(self):
        b = ShiftBuilder(REF_DATE, "split_bucket_acts")
        b.add_work_period(
            "2026-02-02 08:00:00", "2026-02-02 08:10:00", productivity=75
        )
        b.add_work_period(
            "2026-02-02 08:15:00", "2026-02-02 08:20:00", productivity=85
        )
        b.build()
        sp = ShiftPattern(b)
        result = sp._yield_day("2026-02-02", Mins(30))
        assert np.isclose(result[16], 39.166666666)

    def test_break_act_not_spanning_full_bucket(self):
        sb = ShiftBuilder(REF_DATE, name="Break within bucket")
        sb.add_work_period(
            start_time="2026-02-02 06:00:00",
            breaks=ShiftBreak("2026-02-02 08:00:00", "2026-02-02 09:00:00"),
            end_time="2026-02-02 14:00:00",
        )
        sb.add_work_period(
            start_time="2026-02-02 15:00:00",
            breaks=ShiftBreak("2026-02-02 16:00:00", "2026-02-02 16:20:00"),
            end_time="2026-02-02 19:00:00",
        )
        sb.build()
        sp = ShiftPattern(sb)
        result = sp._yield_day("2026-02-23", Mins(30))
        assert result[31] == 100  # Make sure shift runs up to break
        assert np.isclose(result[32], 33.333333333)
        assert result[33] == 100  # Make sure next shift is not lost
        assert np.isclose(result.sum(), 2133.333333333333)  # Whole day adds up


# ===========================================================================
# Integration – end-to-end scenarios
# ===========================================================================


class TestIntegration:
    def test_4_day_continental_pattern(self):
        """4-on / 4-off continental-style schedule."""
        b = ShiftBuilder(REF_DATE, "Continental")
        for i in range(4):
            d = REF_DT + dt.timedelta(days=i)
            b.add_work_period(
                start_time=d.replace(hour=6),
                end_time=d.replace(hour=18),
            )
        for i in range(4, 8):
            b.add_downday(REF_DT + dt.timedelta(days=i))
        b.build()
        assert len(b._shift_days) == 8

    def test_night_shift_only_pattern(self):
        """22:00–06:00 overnight all week Mon–Fri."""
        b = ShiftBuilder(REF_DATE, "Night")
        for i in range(5):
            start = REF_DT + dt.timedelta(days=i)
            end = start + dt.timedelta(days=1)
            b.add_work_period(
                start_time=start.replace(hour=22),
                end_time=end.replace(hour=6),
            )
        b.add_downday(REF_DT + dt.timedelta(days=6))
        b.add_downday(REF_DT + dt.timedelta(days=7))
        b.build()
        assert b._is_built

    def test_full_save_load_pattern_equivalence(self, tmp_path):
        """Saved and loaded pattern should have identical period data."""
        b = built_simple_builder()
        fp = tmp_path / "equiv.json"
        b.save_pattern(fp)
        loaded = ShiftBuilder._load_pattern(fp)

        for orig_day, load_day in zip(
            b._shift_days, loaded._shift_days, strict=True
        ):
            assert len(orig_day.periods) == len(load_day.periods)
            for op, lp in zip(orig_day.periods, load_day.periods, strict=True):
                assert op["prod"] == lp["prod"]
                assert op["start"] == lp["start"]
                assert op["end"] == lp["end"]

    def test_pattern_with_break_saved_and_reloaded(self, tmp_path):
        b = ShiftBuilder(REF_DATE, "BreakRoundTrip")
        brk = ShiftBreak(
            "2026-02-02 10:00:00", "2026-02-02 10:30:00", productivity=50
        )
        b.add_work_period(
            "2026-02-02 06:00:00", "2026-02-02 18:00:00", breaks=brk
        )
        for i in range(1, 7):
            b.add_downday(REF_DT + dt.timedelta(days=i))
        b.build()

        fp = tmp_path / "break.json"
        b.save_pattern(fp)
        sp = ShiftPattern.load_from_file(fp)
        assert sp.name == "BreakRoundTrip"

    def test_productivity_values_preserved_across_periods(self):
        """All periods should have productivity values of 0 or 100 only
        for a standard Mon-Fri pattern."""
        b = built_simple_builder()
        for day in b._shift_days:
            for period in day.periods:
                assert period["prod"] in (0, 100)

    def test_non_standard_productivity_preserved(self):
        """A custom productivity of 75 should survive build."""
        b = ShiftBuilder(REF_DATE, "Slow")
        b.add_work_period(
            "2026-02-02 06:00:00", "2026-02-02 18:00:00", productivity=75
        )
        for i in range(1, 7):
            b.add_downday(REF_DT + dt.timedelta(days=i))
        b.build()
        prods = [p["prod"] for p in b._shift_days[0].periods]
        assert 75 in prods
