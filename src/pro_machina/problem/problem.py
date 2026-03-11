import datetime as dt

from ..config import Config
from ..durations import Duration
from ..exceptions import ProblemError
from ..util import parse_datetime
from .forecasts import DemandForecast
from .machines import BatchMachine, ContinuousMachine, _Machine


class Problem:
    def __init__(
        self,
        start_time: str | dt.datetime,
        length: Duration,
        config: Config | None = None,
    ):
        if config is None:
            self.config = Config()
        else:
            self.config = config

        self.start_time = parse_datetime(start_time)
        self.length = length

        self._end_time = self.start_time + dt.timedelta(
            seconds=self.length.to_seconds()
        )
        self._forecast: DemandForecast | None = None

        # Flags
        self._is_built = False

        # Containers
        self._machines: dict[int, _Machine] = {}

    def add_machine(self, machine: BatchMachine | ContinuousMachine) -> None:
        if not isinstance(machine, _Machine):
            raise TypeError(
                "Can only add types: ContinuousMachine and BatchMachine"
            )
        self._machines[machine._id] = machine

    def set_forecast(self, forecast: DemandForecast):
        self._forecast = forecast

    def build(self) -> None:
        if self._forecast is None:
            raise ProblemError("No demand forecast has been set")
        self._forecast._build(self.start_time, self._end_time, self.config)
        self._is_built = True

    def solve(self) -> None:
        return
