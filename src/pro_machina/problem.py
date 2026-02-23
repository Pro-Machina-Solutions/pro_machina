from .config import Config
from .util import DT, _parse_datetime


class Problem:
    def __init__(self, start_time: DT, config: Config | None = None):
        if config is None:
            self.config = Config()
        else:
            self.config = config

        self.start_time = _parse_datetime(start_time)
