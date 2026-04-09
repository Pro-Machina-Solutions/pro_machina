import datetime as dt
from warnings import warn

import numpy as np
import numpy.typing as npt

import pro_machina

from ..config import Config
from ..durations import Duration
from ..exceptions import ProblemError
from ..util import as_day_start, parse_datetime
from .forecasts import DemandForecast
from .machines import BatchMachine, ContinuousMachine, _Machine
from .stocks import InboundStock, StockHolding


class Problem:
    def __init__(
        self,
        start_time: str | dt.datetime,
        length: Duration,
        config: Config | None = None,
    ):
        if config is not None:
            self.config = config
        else:
            self.config = Config()

        self._user_start_time = parse_datetime(start_time)
        self._start = as_day_start(self._user_start_time)
        self._end = self._start + dt.timedelta(seconds=length.to_seconds())
        self._duration_secs = (self._end - self._start).total_seconds()

        # Flags
        self._is_built = False

        # Containers
        self._forecast: DemandForecast | None = None
        self._machines: dict[int, _Machine] = {}
        self._starting_stocks: dict[int, StockHolding] = {}
        self._inbound_stock: dict[int, InboundStock] = {}

        self._machine_base_productivity: dict[
            int, npt.NDArray[np.float64]
        ] = {}

    def add_machine(self, machine: BatchMachine | ContinuousMachine) -> None:
        if not isinstance(machine, _Machine):
            raise TypeError(
                "Can only add types: ContinuousMachine and BatchMachine"
            )

        if not machine._shifts and not pro_machina.options["silence_warnings"]:
            warn(
                "\n"
                + f"No shift pattern added for {machine.name}. It's assumed to"
                " always be running",
                stacklevel=2,
            )
        self._machines[machine._id] = machine

    def add_stock(self, stock: StockHolding) -> None:
        self._starting_stocks[stock._id] = stock

    def add_inbound_stock(self, inbound: InboundStock) -> None:
        self._inbound_stock[inbound._id] = inbound

    def set_forecast(self, forecast: DemandForecast):
        self._forecast = forecast

    def build(self) -> None:
        if self._forecast is None:
            raise ProblemError("No demand forecast has been set")
        self._forecast._build(self)

        for machine_id, machine in self._machines.items():
            self._machine_base_productivity[machine_id] = (
                machine._build_shift_productivity(self)
            )
        self._is_built = True

    def solve(self) -> None:
        if not self._is_built:
            raise ProblemError("The problem has not been built")
        payload = {}
