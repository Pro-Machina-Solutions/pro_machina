import datetime as dt

from pro_machina.durations import Duration

from ...util import parse_datetime
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
        start_date: str | dt.datetime | dt.date | None = None,
        end_date: str | dt.datetime | dt.date | None = None,
    ) -> None:
        if product is not None:
            check_continuous_prod_only(self, product)
        if machine is not None:
            check_continuous_machine_only(self, machine)
        self.min_time = min_time
        self.product = product
        self.machine = machine

        if start_date is not None:
            self.start_date = parse_datetime(start_date)
        else:
            self.start_date = None
        if end_date is not None:
            self.end_date = parse_datetime(end_date)
        else:
            self.end_date = None

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
            "start_date": self.start_date,
            "end_date": self.end_date,
        }

    def __repr__(self) -> str:
        prod = self.product.name if self.product is not None else "All"
        mach = self.machine.name if self.machine is not None else "All"
        return (
            f"<{self.__class__.__name__}. Product: {prod}, Machine: {mach},"
            f" Run time: {self.min_time}, Start date: {self.start_date},"
            f" End date: {self.end_date}>"
        )


class MaxProductionTime(HardConstraint):
    def __init__(
        self,
        max_time: Duration,
        product: ContinuousProduct | None = None,
        machine: ContinuousMachine | None = None,
        start_date: str | dt.datetime | dt.date | None = None,
        end_date: str | dt.datetime | dt.date | None = None,
    ) -> None:
        if product is not None:
            check_continuous_prod_only(self, product)
        if machine is not None:
            check_continuous_machine_only(self, machine)
        self.max_time = max_time
        self.product = product
        self.machine = machine

        if start_date is not None:
            self.start_date = parse_datetime(start_date)
        else:
            self.start_date = None
        if end_date is not None:
            self.end_date = parse_datetime(end_date)
        else:
            self.end_date = None

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
            "start_date": self.start_date,
            "end_date": self.end_date,
        }

    def __repr__(self) -> str:
        prod = self.product.name if self.product is not None else "All"
        mach = self.machine.name if self.machine is not None else "All"
        return (
            f"<{self.__class__.__name__}. Product: {prod}, Machine: {mach},"
            f" Run time: {self.max_time}, Start date: {self.start_date},"
            f" End date: {self.end_date}>"
        )


class SeasonalProduction(HardConstraint):
    def __init__(
        self,
        start_date: str | dt.datetime | dt.date,
        end_date: str | dt.datetime | dt.date,
        product: _Product | None = None,
        machine: _Machine | None = None,
    ) -> None:
        self.start_date = parse_datetime(start_date)
        self.end_date = parse_datetime(end_date)
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
            "start_date": self.start_date,
            "end_date": self.end_date,
        }


class SlowedProduction(HardConstraint):
    def __init__(
        self,
        start_date: str | dt.datetime | dt.date,
        end_date: str | dt.datetime | dt.date,
        percentage_of_normal: int,
        product: ContinuousProduct | None = None,
        machine: ContinuousMachine | None = None,
    ):

        self.start_date = parse_datetime(start_date)
        self.end_date = parse_datetime(end_date)
        self.product = product
        self.machine = machine
        self.percentage_of_normal = percentage_of_normal

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
            "name": "SLOWED_PRODUCTION",
            "start_date": self.start_date,
            "end_date": self.end_date,
        }


__all__ = ["MinProductionTime", "MaxProductionTime", "SeasonalProduction"]
