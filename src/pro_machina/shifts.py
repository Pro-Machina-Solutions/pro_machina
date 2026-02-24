import datetime as dt
import json
import os
from dataclasses import dataclass
from typing import Self

from .exceptions import ShiftDefinitionError, ShiftIntegrityError
from .util import _parse_datetime, as_midnight


@dataclass
class ShiftBreak:
    """Define a period within a working shift where production is reduced"""

    start: str | dt.datetime
    end: str | dt.datetime
    productivity: int = 0


class _ShiftDay:
    def __init__(self) -> None:
        self.periods = []

    def add_period(self, period: dict) -> None:
        self.periods.append(period)

    def validate(self) -> None:
        if not self.periods:
            raise ShiftDefinitionError(
                "No hours are registered for this shift"
            )

        start_time: dt.datetime = self.periods[0]["start"]

        if start_time != as_midnight(start_time.date()):
            raise ShiftIntegrityError(
                "The shift day does not start at midnight"
            )

        for i in range(len(self.periods) - 1):
            if self.periods[i]["end"] != self.periods[i + 1]["start"]:
                raise ShiftIntegrityError(
                    (
                        "Non-contiguous shift block encountered between: \n"
                        f"{self.periods[i]} and \n{self.periods[i + 1]}"
                    ).lstrip()
                )
            if self.periods[i]["end"] < self.periods[i]["start"]:
                raise ShiftDefinitionError(
                    f"Period ends before it starts:\n{self.periods[i]}"
                )

        if self.periods[-1]["end"] < self.periods[-1]["start"]:
            raise ShiftDefinitionError(
                f"Period ends before it starts:\n{self.periods[i]}"
            )

        if self.periods[-1]["end"] != as_midnight(
            start_time + dt.timedelta(days=1)
        ):
            raise ShiftIntegrityError(
                (
                    "The following shift does not run until midnight:"
                    f" {self.periods[-1]['end']}"
                ).lstrip()
            )

    def for_json(self) -> list[dict]:
        rtn = []
        for period in self.periods:
            period["start"] = period["start"].strftime("%Y-%m-%d %H:%M:%S")
            period["end"] = period["end"].strftime("%Y-%m-%d %H:%M:%S")
            rtn.append(period)
        return rtn

    @classmethod
    def from_json(cls, data: list[dict]) -> Self:
        rtn = cls()
        for row in data:
            rtn.add_period(
                {
                    "start": dt.datetime.fromisoformat(row["start"]),
                    "end": dt.datetime.fromisoformat(row["end"]),
                    "prod": row["prod"],
                }
            )
        return rtn

    def __repr__(self) -> str:
        rtn = "<ShiftDay:\n"
        to_join = []
        for period in self.periods:
            to_join.append(
                f"    [start: {period['start']}, end: {period['end']},"
                f" prod: {period['prod']}]"
            )
        to_join.append(">")
        rtn += "\n".join(to_join)
        return rtn


class ShiftBuilder:
    def __init__(self, ref_start_date: str | dt.datetime, name: str) -> None:
        """Class to build up work periods into a cohesive shift pattern

        In order to build a shift pattern, concrete dates are required which
        represent an example repeating cycle at some point in the past.

        For example, if your facility typically runs from Monday to Sunday,
        with shifts on Monday through Friday, with weekends off, you could
        set this date as any Monday in the calendar that is in the past.

        All subsequent periods of activity must then be defined in reference
        to this date, and must form a contiguous block of days. So in our
        example of Monday-Friday working, one could pick 2026-02-02 as the
        reference date. All periods of activity must then be defined through
        to Sunday 2026-02-08. It is important that both Saturday and Sunday
        are defined using `.add_downday()` such that the pattern covers the
        entire repeating period of the shift pattern. Additionally, if there
        are any days in the middle of the period for which there is no
        activity, you must also add these into the pattern.

        NOTE: in the case of patterns that do not repeat on a 7 day cycle, for
        example with continental shifts where adjacent weeks will have
        different days of activity, it is important that the reference date
        given is aligned correctly to the actual cycle to ensure that the
        pattern will align with the actual working calendar.

        Once the pattern is established for one cycle, it can then be applied
        to any period in the future; the representative dates will be
        abstracted away from that point forwards in the pattern and will
        assume the actual dates in your problem setup.

        Parameters
        ----------
        ref_start_date : str | dt.datetime
            A date or datetime representing a start date for this pattern.
            This does not have to be the same start date as the time period
            you are going to solve for. Rather, it needs to be a
            representative date to act as a datum for the pattern itself.
        name : str
            A descriptive name for the shift pattern
        """
        self.name = name
        self.ref_start_date = _parse_datetime(ref_start_date).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        self._shift_periods: list[dict] = []
        self._shift_days: list[_ShiftDay] = []
        self._day_span: int = 0
        self._is_built = False

    def add_work_period(
        self,
        start_time: str | dt.datetime,
        end_time: str | dt.datetime,
        breaks: ShiftBreak | list[ShiftBreak] = None,
        productivity: int = 100,
    ) -> None:
        """Add a period of productivity to the shift pattern

        Parameters
        ----------
        start_time : str | dt.datetime
            The start time of activity within this shift period
        breaks : ShiftBreak | list[ShiftBreak]
            Optional break periods in which a machine is either running at a
            reduced rate of productivity or turned off completely
        end_time : str | dt.datetime
            The end time of the activity within this shift period
        productivity : int, optional
            The percentage running speed of the machine during normal shift
            hours, by default 100

        Raises
        ------
        ValueError
            Productivity percentges are not specified as being between
            0 and 100
        ShiftDefinitionError
            A user error has been made in the definition of the shift pattern
        ShiftIntegrityError
            An error occurred whilst trying to finalise the shift pattern
            build
        """
        if self._is_built:
            raise ValueError("Cannot add work periods to a finalised shift")

        if breaks is None:
            breaks = []
        elif isinstance(breaks, ShiftBreak):
            breaks = [breaks]

        if not all(isinstance(_break, ShiftBreak) for _break in breaks):
            raise TypeError("Incorrect type supplied for a ShiftBreak")

        if not 0 <= productivity <= 100:
            raise ValueError("Productivity must be between 0-100%")

        for _break in breaks:
            _break.start = _parse_datetime(_break.start)
            _break.end = _parse_datetime(_break.end)
            if not 0 <= _break.productivity <= 100:
                raise ValueError("Break productivity must be between 0-100%")

        start_time = _parse_datetime(start_time)
        end_time = _parse_datetime(end_time)
        self._shift_periods.append(
            {
                "start": start_time,
                "breaks": breaks,
                "end": end_time,
                "is_down_day": False,
                "prod": productivity,
            }
        )

    def add_downday(self, date: str | dt.datetime) -> None:
        """Stipulate a full day of zero productivity

        Parameters
        ----------
        date : str | dt.datetime
            The date for which there is no productivity
        """
        if self._is_built:
            raise ValueError("Cannot add down days to a finalised shift")

        date = _parse_datetime(date)
        self._shift_periods.append({"start": date, "is_down_day": True})

    def _process_down_day(
        self, shift_day: _ShiftDay, rolling_dt: dt.datetime
    ) -> tuple[_ShiftDay, dt.datetime]:

        day_end = as_midnight(rolling_dt + dt.timedelta(days=1))

        shift_day.add_period(
            {
                "start": rolling_dt,
                "end": day_end,
                "prod": 0,
            }
        )
        self._shift_days.append(shift_day)

        # Automatically roll over to next day
        rolling_dt = day_end
        shift_day = _ShiftDay()

        return shift_day, rolling_dt

    def _process_breaks(
        self, this: dict, shift_day: _ShiftDay, rolling_dt: dt.datetime
    ) -> tuple[_ShiftDay, dt.datetime]:

        _break: ShiftBreak
        for b, _break in enumerate(this["breaks"]):
            day_end = as_midnight(this["start"] + dt.timedelta(days=1))

            if _break.start > day_end:
                # Break starts past midnight. Tie up the current day
                shift_day.add_period(
                    {
                        "start": this["start"],
                        "end": day_end,
                        "prod": this["prod"],
                    }
                )
                self._shift_days.append(shift_day)
                rolling_dt = day_end

                # Start the next day in production mode until break
                shift_day = _ShiftDay()
                shift_day.add_period(
                    {
                        "start": rolling_dt,
                        "end": _break.start,
                        "prod": this["prod"],
                    }
                )
                shift_day.add_period(
                    {
                        "start": _break.start,
                        "end": _break.end,
                        "prod": _break.productivity,
                    }
                )
                rolling_dt = _break.end

            else:
                if b == 0:
                    # First break of the day, contained within the current day
                    shift_day.add_period(
                        {
                            "start": this["start"],
                            "end": _break.start,
                            "prod": this["prod"],
                        }
                    )
                else:
                    # Second or more break of the day
                    # Push at full productivity until the break starts
                    shift_day.add_period(
                        {
                            "start": rolling_dt,
                            "end": _break.start,
                            "prod": this["prod"],
                        }
                    )
                rolling_dt = _break.start

                if this["start"].date() != _break.end.date():
                    # Break spans over the change in days. Tie up the day and
                    # start next day within break
                    shift_day.add_period(
                        {
                            "start": _break.start,
                            "end": day_end,
                            "prod": _break.productivity,
                        }
                    )
                    self._shift_days.append(shift_day)
                    rolling_dt = day_end

                    # Start the next day in a break
                    shift_day = _ShiftDay()
                    shift_day.add_period(
                        {
                            "start": rolling_dt,
                            "end": _break.end,
                            "prod": _break.productivity,
                        }
                    )
                    rolling_dt = _break.end
                else:
                    # Break is fully contained in current day
                    shift_day.add_period(
                        {
                            "start": _break.start,
                            "end": _break.end,
                            "prod": _break.productivity,
                        }
                    )
                    rolling_dt = _break.end

        return shift_day, rolling_dt

    def _close_work_period(
        self,
        this: dict,
        next: dict | None,
        shift_day: _ShiftDay,
        rolling_dt: dt.datetime,
    ) -> tuple[_ShiftDay, dt.datetime]:
        # Finish whatever period we might be in
        shift_day.add_period(
            {
                "start": rolling_dt,
                "end": this["end"],
                "prod": this["prod"],
            }
        )
        rolling_dt = this["end"]

        if next is not None and next["start"].date() != this["end"].date():
            # Close off the current day
            day_end = as_midnight(this["end"] + dt.timedelta(days=1))

            if this["end"] < day_end:
                shift_day.add_period(
                    {
                        "start": this["end"],
                        "end": day_end,
                        "prod": 0,
                    }
                )
            self._shift_days.append(shift_day)
            rolling_dt = day_end
            shift_day = _ShiftDay()

        elif next is not None:
            # Push up to the next period
            shift_day.add_period(
                {
                    "start": this["end"],
                    "end": next["start"],
                    "prod": 0,
                }
            )
            rolling_dt = next["start"]

        else:
            # Last period of the entire pattern
            shift_day.add_period(
                {
                    "start": rolling_dt,
                    "end": (
                        as_midnight(rolling_dt.date() + dt.timedelta(days=1))
                    ),
                    "prod": 0,
                }
            )
            self._shift_days.append(shift_day)

        return shift_day, rolling_dt

    def _validate_work_period(self, period: dict) -> None:

        if period["is_down_day"]:
            return

        if period["end"] < period["start"]:
            raise ShiftDefinitionError(
                f"Work period cannot end before it starts:\n{period}"
            )

        if (period["end"] - period["start"]).days > 1:
            raise ShiftDefinitionError(
                f"Work period must span no more than 24 hours:\n{period}"
            )

        if period["breaks"]:
            period["breaks"] = sorted(period["breaks"], key=lambda x: x.start)

        for i, _break in enumerate(period["breaks"]):
            if _break.start < period["start"] or _break.end > period["end"]:
                raise ShiftDefinitionError(
                    f"Break not contained within working hours:\n{_break}"
                )
            if _break.end < _break.start:
                raise ShiftDefinitionError(
                    f"Break cannot end before it starts:\n{_break}"
                )
            for j, other in enumerate(period["breaks"]):
                if i == j:
                    continue
                if (other.start < _break.end and other.end > _break.end) or (
                    _break.start < other.start and other.end < _break.end
                ):
                    raise ShiftDefinitionError(
                        f"Break periods are overlapping:\n{_break}\n{other}"
                    )

    def build(self) -> None:
        """Finalise the shift pattern to be used in the solver

        This function will attempt to take all periods of defined work
        activity and form a completely contiguous description of machine
        output from the satrt date through to the end date

        Raises
        ------
        ValueError
            Raised either when attempting to finalise a pattern more than once
            or when defining productivity percentages outside of range
        ShiftDefinitionError
            The user has incorrectly defined some aspect of their shift
            pattern
        ShiftIntegrityError
            It was not possible to create a coherent, contiguous description
            of shift activities for the period
        """

        if self._is_built:
            raise ValueError("The ShiftBuilder has already been finalised")

        self._shift_periods.sort(key=lambda x: x["start"])

        rolling_dt = self.ref_start_date
        shift_day = _ShiftDay()

        first_shift: bool = True

        for i, this in enumerate(self._shift_periods):
            self._validate_work_period(this)

            try:
                next = self._shift_periods[i + 1]
            except IndexError:
                next = None

            if this["start"].date() != rolling_dt.date() and first_shift:
                # We will not make an assumption on behalf of the user
                raise ShiftDefinitionError(
                    (
                        "The date of the first shift activity of this pattern"
                        " does not match the reference start date. If no shift"
                        " activity is planned for this day, use"
                        " `add_downday()` to fill in any gaps."
                    ).lstrip()
                )
            elif this["start"].date() != rolling_dt.date() and not first_shift:
                # Again, we will not presume to fill the missing day(s) in the
                # middle of the pattern
                raise ShiftDefinitionError(
                    "A day is missing/undefined within the shift pattern"
                )

            first_shift = False

            if this["is_down_day"]:
                shift_day, rolling_dt = self._process_down_day(
                    shift_day, rolling_dt
                )
                continue

            if this["start"] >= rolling_dt:
                if this["start"] != rolling_dt:
                    # Takes us from start of day until first activity
                    shift_day.add_period(
                        {
                            "start": rolling_dt,
                            "end": this["start"],
                            "prod": 0,
                        }
                    )

                if not this["breaks"]:
                    if this["end"].date() == this["start"].date():
                        end_day_end = as_midnight(
                            this["end"] + dt.timedelta(days=1)
                        )
                        shift_day.add_period(
                            {
                                "start": this["start"],
                                "end": this["end"],
                                "prod": this["prod"],
                            }
                        )
                        if this["end"] < end_day_end:
                            # Close off the day fully
                            shift_day.add_period(
                                {
                                    "start": this["end"],
                                    "end": end_day_end,
                                    "prod": 0,
                                }
                            )
                            self._shift_days.append(shift_day)
                            rolling_dt = end_day_end
                            shift_day = _ShiftDay()
                            continue
                    else:
                        # Roll over to the next day

                        day_end = as_midnight(
                            this["start"] + dt.timedelta(days=1)
                        )
                        shift_day.add_period(
                            {
                                "start": this["start"],
                                "end": day_end,
                                "prod": this["prod"],
                            }
                        )

                        self._shift_days.append(shift_day)
                        rolling_dt = day_end
                        shift_day = _ShiftDay()

                        shift_day, rolling_dt = self._close_work_period(
                            this, next, shift_day, rolling_dt
                        )
                        continue
                else:
                    shift_day, rolling_dt = self._process_breaks(
                        this, shift_day, rolling_dt
                    )

                shift_day, rolling_dt = self._close_work_period(
                    this, next, shift_day, rolling_dt
                )

        self._validate_pattern()
        self._is_built = True

    def _validate_pattern(self) -> None:
        curr_end = self._shift_days[0].periods[-1]["end"]
        for i, shift in enumerate(self._shift_days):
            shift.validate()
            if i > 0:
                if shift.periods[0]["start"] != curr_end:
                    raise ShiftIntegrityError(
                        "Shift pattern is not contiguous in days: \n{shift}"
                    )
                curr_end = shift.periods[-1]["end"]

    def save_pattern(self, filepath: str | os.PathLike) -> None:
        """Save pattern for later use

        Parameters
        ----------
        filepath : str | os.PathLike
            The location to save the pattern in JSON format

        Raises
        ------
        ShiftError
            Raised if the ShiftBuilder has not been finalised with `.build()`
        """
        if not self._is_built:
            raise ValueError(
                "Shift pattern has not been finalised. Call .build()"
            )
        self._validate_pattern()
        data = [day.for_json() for day in self._shift_days]
        out = {
            "name": self.name,
            "ref_start_date": self.ref_start_date.strftime("%Y-%m-%d"),
            "created": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data": data,
        }
        with open(filepath, "w") as outfile:
            json.dump(out, outfile, indent=4)

    @classmethod
    def _load_pattern(cls, filepath: str | os.PathLike) -> Self:
        with open(filepath) as infile:
            raw = json.load(infile)
            rtn = cls(ref_start_date=raw["ref_start_date"], name=raw["name"])
            for row in raw["data"]:
                rtn._shift_days.append(_ShiftDay.from_json(row))
            rtn._validate_pattern()
            rtn._is_built = True
        return rtn


class ShiftPattern:
    def __init__(self, builder: ShiftBuilder) -> None:
        """Instantiate a ShiftPattern directly from a finalised ShiftBuilder

        Parameters
        ----------
        builder : ShiftBuilder
            A finalised ShiftBuilder object that has been `.built()`

        Raises
        ------
        ValueError
            The ShiftBuilder has not been finalised
        """
        if not builder._is_built:
            raise ValueError(
                "Shift pattern has not been finalised. Call .build()"
            )
        self._builder = builder
        self.name = self._builder.name

    @classmethod
    def load_from_file(cls, filepath: str | os.PathLike) -> Self:
        """Load a shift pattern from a pre-existing file

        Parameters
        ----------
        filepath : str | os.PathLike
            The location of the JSON file storing the shift data

        Returns
        -------
        Self
            A complete and validated ShiftPattern
        """
        builder = ShiftBuilder._load_pattern(filepath)
        return cls(builder=builder)

    def _parse_to_secs(self):
        pass
