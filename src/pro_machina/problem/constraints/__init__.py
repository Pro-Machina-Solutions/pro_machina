from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pro_machina.problem.products import _Product


class Constraint(ABC):
    @abstractmethod
    def set_product(self, _Product) -> None: ...

    def __hash__(self):
        return hash(type(self).__name__)

    def __eq__(self, other: object):
        if not isinstance(other, HardConstraint):
            raise NotImplementedError
        return hash(type(self).__name__) == hash(type(other).__name__)


class HardConstraint(Constraint):
    def set_product(self, _Product):
        return None


class SoftConstraint(Constraint):
    def set_product(self, _Product):
        return None


class AdvancedConstraint:
    pass
