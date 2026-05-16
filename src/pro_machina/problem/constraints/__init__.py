from __future__ import annotations

from abc import ABCMeta, abstractmethod
from collections.abc import Callable
from typing import TYPE_CHECKING

from ...exceptions import ConstraintError

if TYPE_CHECKING:
    from ..machines import ContinuousMachine, _Machine
    from ..products import ContinuousProduct, _Product


class Constraint(metaclass=ABCMeta):
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
        return hash(type(self).__name__) == hash(type(other).__name__)


class HardConstraint(Constraint):
    def _set_product(self, _Product):
        pass

    def _set_machine(self, _Machine):
        pass

    def _for_payload(self):
        pass


class SoftConstraint(Constraint):
    def _set_product(self, _Product):
        return None

    def _set_machine(self, _Machine):
        return None


from .hard_constraints import MaxProductionTime, MinProductionTime
