import datetime as dt


def parse_datetime(_dt: str | dt.date) -> dt.datetime:
    if isinstance(_dt, str):
        _dt = dt.datetime.fromisoformat(_dt)

    if not isinstance(_dt, dt.datetime):
        raise TypeError("Not a valid datetime")

    return _dt


def to_str_date(_dt: str | dt.date | dt.datetime) -> str:
    if isinstance(_dt, str):
        rtn = dt.datetime.fromisoformat(_dt).strftime("%Y-%m-%d")
    else:
        rtn = _dt.strftime("%Y-%m-%d")
    return rtn


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


class Singleton(type):
    _instances: dict[type, object] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
