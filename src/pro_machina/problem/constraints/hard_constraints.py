import datetime as dt

from pro_machina.durations import Duration
from pro_machina.exceptions import ConstraintError

from ..constraints import HardConstraint
from ..products import ContinuousProduct, _Product


class MinProductionTime(HardConstraint):
    def __init__(
        self, min_time: Duration, product: ContinuousProduct | None = None
    ) -> None:
        if product is not None and not isinstance(product, ContinuousProduct):
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
        self, max_time: Duration, product: ContinuousProduct | None = None
    ) -> None:
        if product is not None and not isinstance(product, ContinuousProduct):
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


class SeasonalProduction(HardConstraint):
    def __init__(
        self,
        start_date: dt.datetime,
        end_date: dt.datetime,
        product: _Product | None = None,
    ) -> None:
        self.start_date = start_date
        self.end_date = end_date
        self.product = product

    def set_product(self, product: _Product) -> None:
        self.product = product


__all__ = ["MinProductionTime", "MaxProductionTime"]
