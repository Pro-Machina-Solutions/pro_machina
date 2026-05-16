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
        return (
            hash(type(self).__name__) == hash(type(other).__name__)
            and self.start_date == other.start_date
        )


class HardConstraint(Constraint):
    pass


class SoftConstraint(Constraint):
    pass


from .hard_constraints import (
    MaxProductionTime,
    MinProductionTime,
    SeasonalProduction,
)
