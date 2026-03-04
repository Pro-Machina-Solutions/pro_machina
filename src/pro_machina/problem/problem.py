import datetime as dt

from pro_machina.config import Config
from pro_machina.util import parse_datetime


class Problem:
    def __init__(
        self, start_time: str | dt.datetime, config: Config | None = None
    ):
        if config is None:
            self.config = Config()
        else:
            self.config = config

        self.start_time = parse_datetime(start_time)
