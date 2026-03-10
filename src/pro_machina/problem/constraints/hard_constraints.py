from pro_machina.durations import Duration
from pro_machina.exceptions import ConstraintError

from ..constraints import HardConstraint
from ..products import ContinuousProduct


class MinProductionTime(HardConstraint):
    def __init__(
        self, min_time: Duration, product: ContinuousProduct | None
    ) -> None:
        if not isinstance(product, ContinuousProduct):
            raise ConstraintError(
                (
                    f"{self.__class__.__name__} cannot be added to"
                    f" {product.__class__.__name__}"
                ).lstrip()
            )
        self.min_time = min_time
        self.product = product

    def set_product(self, product: ContinuousProduct) -> None:
        if not isinstance(product, ContinuousProduct):
            raise ConstraintError(
                (
                    f"{self.__class__.__name__} cannot be added to"
                    f" {product.__class__.__name__}"
                ).lstrip()
            )
        self.product = product


class MaxProductionTime(HardConstraint):
    def __init__(
        self, max_time: Duration, product: ContinuousProduct | None
    ) -> None:
        if not isinstance(product, ContinuousProduct):
            raise ConstraintError(
                (
                    f"{self.__class__.__name__} cannot be added to"
                    f" {product.__class__.__name__}"
                ).lstrip()
            )
        self.max_time = max_time
        self.product = product

    def set_product(self, product: ContinuousProduct) -> None:
        if not isinstance(product, ContinuousProduct):
            raise ConstraintError(
                (
                    f"{self.__class__.__name__} cannot be added to"
                    f" {product.__class__.__name__}"
                ).lstrip()
            )
        self.product = product


__all__ = ["MinProductionTime", "MaxProductionTime"]
