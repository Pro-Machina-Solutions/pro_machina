import datetime as dt

from ..config import Config
from ..util import parse_datetime
from .machines import BatchMachine, ContinuousMachine, _Machine


class Problem:
    def __init__(
        self, start_time: str | dt.datetime, config: Config | None = None
    ):
        if config is None:
            self.config = Config()
        else:
            self.config = config

        self.start_time = parse_datetime(start_time)

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

    def build(self) -> None:
        self._is_built = True

    def solve(self) -> None:
        return
