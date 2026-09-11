from __future__ import annotations

import datetime as dt
from abc import ABCMeta, abstractmethod
from copy import deepcopy
from enum import Enum
from typing import TYPE_CHECKING, Any, Self

if TYPE_CHECKING:
    from ..machines import _Machine
    from ..products import _Product


class ConstraintLevel(Enum):
    UNSET = 0
    DEFAULT = 1
    PRODUCT = 2
    PRODUCT_GROUP = 3
    MACHINE = 4
    MACHINE_GROUP = 5
    PROBLEM = 6


class Constraint(metaclass=ABCMeta):
    start_date: dt.datetime | None
    end_date: dt.datetime | None
    product: _Product | None
    machine: _Machine | None
    _level: int

    @abstractmethod
    def _set_product(self, product: _Product | None) -> None: ...

    @abstractmethod
    def _set_machine(self, machine: _Machine | None) -> None: ...

    @abstractmethod
    def _set_level(self, int) -> None: ...

    def _serialise(self) -> dict[str, Any]:
        fields = deepcopy(self.__dict__)
        fields["name"] = self.__class__.__name__

        if self.product is not None:
            fields["product"] = self.product._id
        else:
            fields["product"] = None

        if self.machine is not None:
            fields["machine"] = self.machine._id
        else:
            fields["machine"] = None

        return fields

    def __hash__(self) -> int:
        return hash(type(self).__name__)

    def __eq__(self, other: object) -> bool:
        return hash(type(self).__name__) == hash(type(other).__name__)


class HardConstraint(Constraint):
    pass


class SoftConstraint(Constraint):
    pass


class ProductOnly(Constraint):
    pass


class MachineOnly(Constraint):
    pass


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
