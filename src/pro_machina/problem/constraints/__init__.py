from __future__ import annotations

import datetime as dt
from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Any

from ...exceptions import ConstraintError

if TYPE_CHECKING:
    from ..machines import _Machine
    from ..products import _Product


class Constraint(metaclass=ABCMeta):
    _id: str
    start_date: dt.datetime | None
    end_date: dt.datetime | None
    product: _Product | None
    machine: _Machine | None

    @abstractmethod
    def _set_product(self, _Product) -> None: ...

    @abstractmethod
    def _set_machine(self, _Machine) -> None: ...

    def _serialise(self) -> dict[str, Any]:
        fields = self.__dict__
        fields["name"] = type(self).__name__

        if self.product is not None:
            fields["product"] = self.product._id
        else:
            fields["product"] = None

        if self.machine is not None:
            fields["machine"] = self.product._id
        else:
            fields["machine"] = None
        return fields


class HardConstraint(Constraint):
    pass


class SoftConstraint(Constraint):
    pass


from ._arbiter import ConstraintArbiter, ConstraintLevel
from .constraint_groupings import (
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
