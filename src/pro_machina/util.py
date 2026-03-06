import datetime as dt


def parse_datetime(_dt: str | dt.date) -> dt.datetime:
    if isinstance(_dt, str):
        _dt = dt.datetime.fromisoformat(_dt)

    if not isinstance(_dt, dt.datetime):
        raise TypeError("Not a valid datetime")

    return _dt


def as_midnight(date: dt.date) -> dt.datetime:
    """Convert a date object to a datetime object

    Parameters
    ----------
    date : dt.date
        The date object to be converted to a datetime object

    Returns
    -------
    dt.datetime
        A datetime representation of the date with 00:00:00 for %H:%M:%S
    """
    return dt.datetime.combine(date, dt.datetime.min.time())
