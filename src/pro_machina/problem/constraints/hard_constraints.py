import datetime as dt

from pro_machina.durations import Duration

from ..constraints import HardConstraint
from ..machines import ContinuousMachine, _Machine
from ..products import ContinuousProduct, _Product
from .type_checkers import (
    check_continuous_machine_only,
    check_continuous_prod_only,
)


class MinProductionTime(HardConstraint):
    def __init__(
        self,
        min_time: Duration,
        product: ContinuousProduct | None = None,
        machine: ContinuousMachine | None = None,
    ) -> None:
        if product is not None:
            check_continuous_prod_only(self, product)
        if machine is not None:
            check_continuous_machine_only(self, machine)
        self.min_time = min_time
        self.product = product
        self.machine = machine

    def _set_product(self, product: ContinuousProduct) -> None:
        check_continuous_prod_only(self, product)
        self.product = product

    def _set_machine(self, machine: ContinuousMachine) -> None:
        check_continuous_machine_only(self, machine)
        self.machine = machine

    def _for_payload(self):
        return {
            "product_id": self.product._id,
            "machine_id": self.machine._id,
            "name": "MAX_PRODUCTION_TIME",
            "time": self.min_time.to_seconds(),
        }


class MaxProductionTime(HardConstraint):
    def __init__(
        self,
        max_time: Duration,
        product: ContinuousProduct | None = None,
        machine: ContinuousMachine | None = None,
    ) -> None:
        if product is not None:
            check_continuous_prod_only(self, product)
        self.max_time = max_time
        self.product = product
        self.machine = machine

    def _set_product(self, product: ContinuousProduct) -> None:
        check_continuous_prod_only(self, product)
        self.product = product

    def _set_machine(self, machine: ContinuousMachine) -> None:
        check_continuous_machine_only(self, machine)
        self.machine = machine

    def _for_payload(self):
        return {
            "product_id": self.product._id,
            "machine_id": self.machine._id,
            "name": "MAX_PRODUCTION_TIME",
            "time": self.max_time.to_seconds(),
        }


class SeasonalProduction(HardConstraint):
    def __init__(
        self,
        start_date: dt.datetime,
        end_date: dt.datetime,
        product: _Product | None = None,
        machine: _Machine | None = None,
    ) -> None:
        self.start_date = start_date
        self.end_date = end_date
        self.product = product
        self.machine = machine

    def _set_product(self, product: _Product) -> None:
        self.product = product

    def _set_machine(self, machine: _Machine) -> None:
        self.machine = machine

    def _for_payload(self):
        return {
            "product_id": self.product._id,
            "machine_id": self.machine._id,
            "name": "SEASONAL_PRODUCTION",
            "start_date": dt.datetime.strftime(self.start_date, "%Y-%m-%d"),
            "end_date": dt.datetime.strftime(self.end_date, "%Y-%m-%d"),
        }


__all__ = ["MinProductionTime", "MaxProductionTime"]
