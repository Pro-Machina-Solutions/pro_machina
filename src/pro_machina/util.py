from __future__ import annotations

import datetime as dt
from functools import cache
from typing import TYPE_CHECKING

from .durations import Duration

if TYPE_CHECKING:
    pass


def parse_datetime(dt_: str | dt.datetime | dt.date) -> dt.datetime:
    """Convert a datetime-like object into a defined datetime

    This is an internal method to suit the purposes of pro_machina and is not
    intended for use outside of this package.

    If given a string, it must be in ISO 8601 format and will return a
    datetime. If given a date object it will return a datetime of midnight at
    the very start of the day. Actual datetime objects fall through unchanged.

    Parameters
    ----------
    dt_ : str | dt.datetime | dt.date
        A datetime-like object

    Returns
    -------
    dt.datetime
        An actual datetime

    Raises
    ------
    TypeError
        A datetime couldn't be parsed from the input
    """
    if isinstance(dt_, str):
        dt_ = dt.datetime.fromisoformat(dt_)

    if not isinstance(dt_, (dt.datetime, dt.date)):
        raise TypeError("Not a valid datetime")

    # Has to be done this way around because dt.datetime is a subclass of
    # dt.date. Do not change this around as it breaks *everything*.
    if not isinstance(dt_, dt.datetime):
        dt_ = dt.datetime.combine(dt_, dt.datetime.min.time())

    return dt_


def to_str_date(dt_: str | dt.date | dt.datetime) -> str:
    """Return the ISO 8601 representation of a date

    This is an internal method to suit the purposes of pro_machina and is not
    intended for use outside of this package.

    Parameters
    ----------
    _dt : str | dt.date | dt.datetime
        A date or datetime-like object

    Returns
    -------
    str
        ISO 8601 date
    """
    if isinstance(dt_, str):
        rtn = dt.datetime.fromisoformat(dt_).strftime("%Y-%m-%d")
    else:
        rtn = dt_.strftime("%Y-%m-%d")
    return rtn


def as_day_start(date: dt.date | dt.datetime | str) -> dt.datetime:
    """Convert a date object to a datetime object

    This is an internal method to suit the purposes of pro_machina and is not
    intended for use outside of this package.

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
    """Bump the datetime to the start of the next day

    This is an internal method to suit the purposes of pro_machina and is not
    intended for use outside of this package.

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
def get_problem_buckets(
    problem_start: dt.datetime, problem_end: dt.datetime, timebucket: Duration
) -> int:
    """Return the total number of time buckets in the problem

    Takes the full duration of the problem and divides it by the duration of
    each time bucket.

    Parameters
    ----------
    problem_start : dt.datetime
        The start datetime of the problem span
    problem_end : dt.datetime
        The end datetime of the problem span
    timebucket : Duration
        The duration that the problem span is divided into

    Returns
    -------
    int
        Total number of time buckets for the problem, each representing a
        segement of the specified duration
    """
    timebucket_secs = int(timebucket.to_seconds())
    tot_problem_secs = (problem_end - problem_start).total_seconds()
    return int(tot_problem_secs / timebucket_secs)


def get_bucket_index(
    problem_start: dt.datetime,
    problem_end: dt.datetime,
    timebucket: Duration,
    timestamp: dt.datetime,
) -> int:
    """Return the closest bucket index for a datetime

    The total time span of a problem is subdivided into equally-sized buckets.
    Based on this, we can determine which index of the resulting array of
    timed activities that a timestamp falls within

    Parameters
    ----------
    problem_start : dt.datetime
        The start datetime of the problem span
    problem_end : dt.datetime
        The end datetime of the problem span
    timebucket : Duration
        The duration that the problem span is divided into
        A datetime stamp within the span of the problem duration
    timestamp : dt.datetime
        The datetime to be given an array index into the problem span

    Returns
    -------
    int
        The related index of the timebucket the timestamp falls within

    Raises
    ------
    ValueError
        The timestamp is outside of the bounds of the problem duration
    """
    num_buckets = get_problem_buckets(problem_start, problem_end, timebucket)
    frac = (timestamp - problem_start).total_seconds() / (
        (problem_end - problem_start).total_seconds()
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
