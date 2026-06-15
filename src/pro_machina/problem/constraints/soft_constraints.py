import datetime as dt
from uuid import uuid4

from ..constraints import SoftConstraint
from ..machines import _Machine
from ..products import ContinuousProduct, _Product


class OverstockingPenalty(SoftConstraint):
    def __init__(
        self,
        value,
        start_date: str | dt.datetime | dt.date | None = None,
        end_date: str | dt.datetime | dt.date | None = None,
        product: ContinuousProduct | None = None,
    ) -> None:
        # Only applies to products
        self._id = uuid4().hex

    def _set_product(self, product: _Product) -> None:
        self.product = product

    def _set_machine(self, machine: _Machine) -> None:
        return None

    def _get_values(self) -> dict[str, float]:
        return {"value": self.value}


__all__ = ["SoftConstraint", "OverstockingPenalty"]
