from __future__ import annotations

import datetime as dt
from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

from ...exceptions import ConstraintError

if TYPE_CHECKING:
    from ..machines import _Machine
    from ..products import _Product


class Constraint(metaclass=ABCMeta):
    start_date: dt.datetime | None
    end_date: dt.datetime | None
    product: _Product | None
    machine: _Machine | None

    @abstractmethod
    def _set_product(self, _Product) -> None: ...

    @abstractmethod
    def _set_machine(self, _Machine) -> None: ...

    @abstractmethod
    def _for_payload(self) -> dict[str, str | float]: ...

    def __hash__(self):
        return hash(type(self).__name__)

    def __eq__(self, other: object):
        if not isinstance(other, Constraint):
            raise NotImplementedError

        try:
            start = self.start_date
        except AttributeError:
            start = None

        try:
            other_start = other.start_date
        except AttributeError:
            other_start = None

        return (
            hash(type(self).__name__) == hash(type(other).__name__)
            and start == other_start
        )


class HardConstraint(Constraint):
    pass


class SoftConstraint(Constraint):
    pass


from .groupings import (
    MutuallyExclusiveMachines,
    PairedMachines,
)
from .hard_constraints import (
    MaxProductionTime,
    MaxProductLifetime,
    MaxStorageCapacity,
    MinProductionTime,
    ReducedProductionPeriod,
    SeasonalProduction,
)
