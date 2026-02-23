import datetime as dt
import json
import os
from dataclasses import dataclass
from typing import Self

from .exceptions import ShiftError
from .util import DT, _parse_datetime, as_dt


@dataclass
class ShiftBreak:
    """Define a period within a working shift where production is reduced"""

    start: DT
    end: DT
    productivity: int = 0


class _ShiftDay:
    def __init__(self) -> None:
        self.periods = []

    def add_period(self, period: dict) -> None:
        self.periods.append(period)

    def check_day_coverage(self):
        if not self.periods:
            raise ShiftError("No hours are registered for this shift")

        start_time: dt.datetime = self.periods[0]["start"]

        if start_time != as_dt(start_time.date()):
            raise ShiftError("The shift day does not start at midnight")

        for i in range(len(self.periods) - 1):
            if self.periods[i]["end"] != self.periods[i + 1]["start"]:
                raise ShiftError(
                    (
                        "Non-contiguous shift block encountered between: "
                        f"{self.periods[i]} and {self.periods[i + 1]}"
                    ).lstrip()
                )
        if self.periods[-1]["end"] != as_dt(start_time + dt.timedelta(days=1)):
            raise ShiftError(
                (
                    "The following shift does not run until midnight: "
                    f"{self.periods[-1]['end']}"
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
                f"    [start: {period['start']}, end: {period['end']}, "
                f"prod: {period['prod']}]"
            )
        to_join.append(">")
        rtn += "\n".join(to_join)
        return rtn


class ShiftBuilder:
    def __init__(self, ref_start_date: DT, name: str) -> None:
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
        to Sunday 2026-02-08. It is important that both Saturday and Sunday are
        defined using `.add_downday()` such that the pattern covers the entire
        repeating period of the shift pattern. Additionally, if there are any
        days in the middle of the period for which there is no activity, you
        must also add these into the pattern.

        NOTE: in the case of patterns that do not repeat on a 7 day cycle, for
        example with continental shifts where adjacent weeks will have
        different days of activity, it is important that the reference date
        given is aligned correctly to the actual cycle to ensure that the
        pattern will align with the actual working calendar.

        Once the pattern is established for one cycle, it can then be applied to
        any period in the future; the representative dates will be abstracted
        away from that point forwards in the pattern and will assume the actual
        dates in your problem setup.

        Parameters
        ----------
        ref_start_date : str | dt.datetime
            A date or datetime representing a start date for this pattern. This
            does not have to be the same start date as the time period you are
            going to solve for. Rather, it needs to be a representative date to
            act as a datum for the pattern itself.
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
        start_time: DT,
        breaks: ShiftBreak | list[ShiftBreak],
        end_time: DT,
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
            The end time of the activity within this shit period
        productivity : int, optional
            The percentage running speed of the machine during normal shift
            hours, by default 100

        Raises
        ------
        ValueError
            Productivity percentges are not specified as being between 0 and 100
        ShiftError
            Any error in the definition of a shift period
        """
        if isinstance(breaks, ShiftBreak):
            breaks = [breaks]

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

    def add_downday(self, date: DT) -> None:
        """Stipulate a full day of zero productivity

        Parameters
        ----------
        date : str | dt.datetime
            The date for which there is no productivity
        """
        date = _parse_datetime(date)
        self._shift_periods.append({"start": date, "is_down_day": True})

    def build(self) -> None:
        self._shift_periods.sort(key=lambda x: x["start"])

        rolling_dt = self.ref_start_date
        shift_day = _ShiftDay()

        for i in range(len(self._shift_periods) - 1):
            this = self._shift_periods[i]
            next = self._shift_periods[i + 1]

            if this["start"].date() != rolling_dt.date():
                # We will not make an assumption on behalf of the user
                raise ShiftError(
                    (
                        "The date of the first shift activity of this pattern "
                        "does not match the reference start date. If no shift "
                        "activity is planned for this day, use `add_downday()`"
                        " to fill in any gaps."
                    ).lstrip()
                )
            if this["is_down_day"]:
                shift_day.add_period(
                    {
                        "start": rolling_dt,
                        "end": as_dt(rolling_dt + dt.timedelta(days=1)),
                        "prod": 0,
                    }
                )
                self._shift_days.append(shift_day)
                rolling_dt = as_dt(rolling_dt + dt.timedelta(days=1))
                shift_day = _ShiftDay()
            else:
                if this["start"] >= rolling_dt:
                    if this["start"] != rolling_dt:
                        shift_day.add_period(
                            {
                                "start": rolling_dt,
                                "end": this["start"],
                                "prod": 0,
                            }
                        )
                    _break: ShiftBreak
                    for _break in this["breaks"]:
                        if _break.start.date() > rolling_dt.date():
                            # Tie up the day
                            shift_day.add_period(
                                {
                                    "start": this["start"],
                                    "end": as_dt(
                                        rolling_dt.date() + dt.timedelta(days=1)
                                    ),
                                    "prod": this["prod"],
                                }
                            )
                            self._shift_days.append(shift_day)
                            rolling_dt = as_dt(
                                rolling_dt.date() + dt.timedelta(days=1)
                            )

                            # start the next day
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
                            shift_day.add_period(
                                {
                                    "start": this["start"],
                                    "end": _break.start,
                                    "prod": this["prod"],
                                }
                            )
                            if this["start"].date() != _break.end.date():
                                # Break spans over the change in days. Tie up
                                # the day and start next day within break
                                shift_day.add_period(
                                    {
                                        "start": _break.start,
                                        "end": as_dt(
                                            rolling_dt.date()
                                            + dt.timedelta(days=1)
                                        ),
                                        "prod": _break.productivity,
                                    }
                                )
                                self._shift_days.append(shift_day)
                                rolling_dt = as_dt(
                                    rolling_dt.date() + dt.timedelta(days=1)
                                )

                                # Start the next day in a break
                                shift_day = _ShiftDay()
                                shift_day.add_period(
                                    {
                                        "start": rolling_dt,
                                        "end": _break.end,
                                        "prod": _break.productivity,
                                    }
                                )
                            else:
                                shift_day.add_period(
                                    {
                                        "start": _break.start,
                                        "end": _break.end,
                                        "prod": _break.productivity,
                                    }
                                )
                                rolling_dt = _break.end
                    if next["start"].date() != this["end"].date():
                        # Tie up the day
                        shift_day.add_period(
                            {
                                "start": rolling_dt,
                                "end": as_dt(
                                    rolling_dt.date() + dt.timedelta(days=1)
                                ),
                                "prod": 0,
                            }
                        )
                        self._shift_days.append(shift_day)
                        rolling_dt = as_dt(
                            rolling_dt.date() + dt.timedelta(days=1)
                        )
                        shift_day = _ShiftDay()
                    else:
                        # First tie up the current shift
                        shift_day.add_period(
                            {
                                "start": rolling_dt,
                                "end": this["end"],
                                "prod": this["prod"],
                            }
                        )
                        rolling_dt = this["end"]
                        # Push up to the next shift start
                        shift_day.add_period(
                            {
                                "start": rolling_dt,
                                "end": next["start"],
                                "prod": 0,
                            }
                        )
                        rolling_dt = next["start"]
        # TODO: Add the last period

        self._validate_pattern()
        self._is_built = True

    def _validate_pattern(self) -> None:
        curr_end = self._shift_days[0].periods[-1]["end"]
        for i, shift in enumerate(self._shift_days):
            shift.check_day_coverage()
            if i > 0:
                if shift.periods[0]["start"] != curr_end:
                    raise ShiftError("Shift pattern is not contiguous in days")
                curr_end = shift.periods[-1]["end"]

    def save_pattern(self, filepath: str | os.PathLike):
        if not self._is_built:
            raise ShiftError("Shift pattern has not been built")
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
    def __init__(self, builder: ShiftBuilder):
        if not builder._is_built:
            raise ValueError(
                "The shift pattern has not been built. Call `.build()`"
            )
        self._builder = builder
        self.name = self._builder.name

    @classmethod
    def load_from_file(cls, filepath: str | os.PathLike) -> Self:
        builder = ShiftBuilder._load_pattern(filepath)
        return cls(builder=builder)

    def _parse_to_secs(self):
        pass
