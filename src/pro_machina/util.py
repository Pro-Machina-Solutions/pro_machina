from __future__ import annotations

import datetime as dt
from functools import cache
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .problem import Problem


def parse_datetime(_dt: str | dt.datetime | dt.date) -> dt.datetime:
    if isinstance(_dt, str):
        _dt = dt.datetime.fromisoformat(_dt)

    if not isinstance(_dt, (dt.datetime, dt.date)):
        raise TypeError("Not a valid datetime")

    # Has to be done this way around because dt.datetime is a subclass of
    # dt.date. Do not change this around as it breaks *everything*.
    if not isinstance(_dt, dt.datetime):
        _dt = dt.datetime.combine(_dt, dt.datetime.min.time())

    return _dt


def to_str_date(_dt: str | dt.date | dt.datetime) -> str:
    """Return the ISO 8601 representation of a date

    Parameters
    ----------
    _dt : str | dt.date | dt.datetime
        A date or datetime-like object

    Returns
    -------
    str
        ISO 8601 date
    """
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
    if isinstance(date, str):
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
    if isinstance(date, str):
        date = parse_datetime(date)
    return dt.datetime.combine(
        as_day_start(date + dt.timedelta(days=1)), dt.datetime.min.time()
    )


@cache
def get_problem_buckets(problem: Problem) -> int:
    """Return the total number of time buckets in the problem

    Takes the full duration of the problem and divides it by the duration of
    each time bucket.

    Parameters
    ----------
    problem : Problem
        The main problem instance

    Returns
    -------
    int
        Total number of time buckets for the problem, each representing a
        segement of the specified duration
    """
    timebucket_secs = int(problem.config._timebucket.to_seconds())
    tot_problem_secs = (problem._end - problem._start).total_seconds()
    return int(tot_problem_secs / timebucket_secs)


def get_bucket_index(
    problem: Problem,
    timestamp: dt.datetime,
) -> int:
    """Return the closest bucket index for a datetime

    The total time span of a problem is subdivided into equally-sized buckets.
    Based on this, we can determine which index of the resulting array of
    timed activities that a timestamp falls within

    Parameters
    ----------
    problem : Problem
        The main problem instance
    timestamp : dt.datetime
        A datetime stamp within the span of the problem duration

    Returns
    -------
    int
        The related index of the timebucket the timestamp falls within

    Raises
    ------
    ValueError
        The timestamp is outside of the bounds of the problem duration
    """
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
