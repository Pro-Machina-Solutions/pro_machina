from __future__ import annotations

import datetime as dt
from functools import cache
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .problem import Problem


def parse_datetime(_dt: str | dt.date | dt.datetime) -> dt.datetime:
    if isinstance(_dt, str):
        _dt = dt.datetime.fromisoformat(_dt)

    if not isinstance(_dt, (dt.datetime, dt.date)):
        raise TypeError("Not a valid datetime")

    return _dt


def to_str_date(_dt: str | dt.date | dt.datetime) -> str:
    if isinstance(_dt, str):
        rtn = dt.datetime.fromisoformat(_dt).strftime("%Y-%m-%d")
    else:
        rtn = _dt.strftime("%Y-%m-%d")
    return rtn


def as_day_start(date: dt.date | dt.datetime | str) -> dt.datetime:
    """Convert a date object to a datetime object.

    Parameters
    ----------
    date : dt.date
        The date object to be converted to a datetime object

    Returns
    -------
    dt.datetime
        A datetime representation of the date with 00:00:00 for %H:%M:%S
    """
    date = parse_datetime(date)
    return dt.datetime.combine(date, dt.datetime.min.time())


def as_day_end(date: dt.date | dt.datetime | str) -> dt.datetime:
    """Bump the datetime to the start of the next day.

    This method will automatically add 1 day onto any datetime and then knock
    it back to the very start of the day, to close off anything that requires
    the previous 24 hours to be complete.

    Parameters
    ----------
    date : dt.date | dt.datetime | str
        The date to be bumped

    Returns
    -------
    dt.datetime
        The knocked-back datetime
    """
    date = parse_datetime(date)
    return dt.datetime.combine(
        as_day_start(date + dt.timedelta(days=1)), dt.datetime.min.time()
    )


@cache
def get_problem_buckets(problem: Problem) -> int:
    timebucket_secs = int(problem.config._timebucket.to_seconds())
    tot_problem_secs = (problem._end - problem._start).total_seconds()
    return int(tot_problem_secs / timebucket_secs)


def get_bucket_index(
    problem: Problem,
    timestamp: dt.datetime,
) -> int:
    num_buckets = get_problem_buckets(problem)
    frac = (timestamp - problem._start).total_seconds() / (
        problem._duration_secs
    )
    if not 0 <= frac <= 1:
        raise ValueError("Timestamp outside of problem range")
    return int(frac * num_buckets)


class Singleton(type):
    _instances: dict[type, object] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
