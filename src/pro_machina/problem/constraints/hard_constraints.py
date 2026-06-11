import datetime as dt
from uuid import uuid4

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
    """Specify the minimum continuous run time of a product or a machine

    **Only applies to Continous Products/Machines**

    This constraint can be applied in multiple ways depending on the desired
    outcome. It could be used to say that Product A, regardless of the machine
    it is produced by, **must** always be produced in a minimum run of
    Hours(4).

    If applied on the machine-level, you could suggest that Machine A must
    never do a production run of **any** product for less than Hours(4).

    Finally, it could be specified for a specific Product-Machine pairing for
    fine control.

    Parameters
    ----------
    value : Duration
        The minimum continuous duration that this product can be produced
    start_date : str | dt.datetime | dt.date | None, optional
        The start date of the constraint consideration, by default None. If
        left as None, it will apply across the entire problem
    end_date : str | dt.datetime | dt.date | None, optional
        The end date of the constraint consideration, by default None. If
        left as None, it will apply across the entire problem
    product : ContinuousProduct | None, optional
        Specify a particular product that this applies to, by default None. If
        left as None, it will be determined by the context in which the
        constraint is specified (on the product-level or machine-level)
    machine : ContinuousMachine | None, optional
        Specify a particular machine that this applies to, by default None. If
        left as None, it will be determined by the context in which the
        constraint is specified (on the product-level or machine-level)

    Raises
    ------
    ConstraintError
        Raised if this is applied to a product or machine that is not
        Continuous
    """

    def __init__(
        self,
        value: Duration,
        start_date: str | dt.datetime | dt.date | None = None,
        end_date: str | dt.datetime | dt.date | None = None,
        product: ContinuousProduct | None = None,
        machine: ContinuousMachine | None = None,
    ) -> None:

        self._set_product(product)
        self._set_machine(machine)

        self.value = value.to_seconds()

        if start_date is not None:
            self.start_date = parse_datetime(start_date)
        else:
            self.start_date = None
        if end_date is not None:
            self.end_date = parse_datetime(end_date)
        else:
            self.end_date = None

    def _set_product(self, product: ContinuousProduct | None) -> None:
        if product is not None:
            check_continuous_prod_only(self, product)
        self.product = product

    def _set_machine(self, machine: ContinuousMachine | None) -> None:
        if machine is not None:
            check_continuous_machine_only(self, machine)
        self.machine = machine

    def __repr__(self) -> str:
        prod = self.product.name if self.product is not None else "All"
        mach = self.machine.name if self.machine is not None else "All"
        return (
            f"<{self.__class__.__name__}. Product: {prod}, Machine: {mach},"
            f" Run time: {self.value}, Start date: {self.start_date},"
            f" End date: {self.end_date}>"
        )


class MaxProductionTime(HardConstraint):
    """Specify the maximum continuous run time of a product or a machine

    **Only applies to Continous Products/Machines**

    This constraint can be applied in multiple ways depending on the desired
    outcome. It could be used to say that Product A, regardless of the machine
    it is produced by, **must** always be produced in a maximum run of
    Hours(12).

    If applied on the machine-level, you could suggest that Machine A must
    never do a production run of **any** product for less than Hours(12).

    Finally, it could be specified for a specific Product-Machine pairing for
    fine control.

    Parameters
    ----------
    value : Duration
        The maximum continuous duration that this product can be produced
    start_date : str | dt.datetime | dt.date | None, optional
        The start date of the constraint consideration, by default None. If
        left as None, it will apply across the entire problem
    end_date : str | dt.datetime | dt.date | None, optional
        The end date of the constraint consideration, by default None. If
        left as None, it will apply across the entire problem
    product : ContinuousProduct | None, optional
        Specify a particular product that this applies to, by default None. If
        left as None, it will be determined by the context in which the
        constraint is specified (on the product-level or machine-level)
    machine : ContinuousMachine | None, optional
        Specify a particular machine that this applies to, by default None. If
        left as None, it will be determined by the context in which the
        constraint is specified (on the product-level or machine-level)

    Raises
    ------
    ConstraintError
        Raised if this is applied to a product or machine that is not
        Continuous
    """

    def __init__(
        self,
        value: Duration,
        start_date: str | dt.datetime | dt.date | None = None,
        end_date: str | dt.datetime | dt.date | None = None,
        product: ContinuousProduct | None = None,
        machine: ContinuousMachine | None = None,
    ) -> None:

        self._set_product(product)
        self._set_machine(machine)

        self.value = value.to_seconds()

        if start_date is not None:
            self.start_date = parse_datetime(start_date)
        else:
            self.start_date = None
        if end_date is not None:
            self.end_date = parse_datetime(end_date)
        else:
            self.end_date = None

    def _set_product(self, product: ContinuousProduct | None) -> None:
        if product is not None:
            check_continuous_prod_only(self, product)
        self.product = product

    def _set_machine(self, machine: ContinuousMachine | None) -> None:
        if machine is not None:
            check_continuous_machine_only(self, machine)
        self.machine = machine

    def __repr__(self) -> str:
        prod = self.product.name if self.product is not None else "All"
        mach = self.machine.name if self.machine is not None else "All"
        return (
            f"<{self.__class__.__name__}. Product: {prod}, Machine: {mach},"
            f" Run time: {self.value}, Start date: {self.start_date},"
            f" End date: {self.end_date}>"
        )


class SeasonalProduction(HardConstraint):
    """Specify a date range in which a product can be produced

    This is useful for promos or events e.g. products that are only produced
    for Christmas should not be produced before November 1st and should not be
    produced after December 23rd (regardless of whether the total demand was
    met by that point or not).

    This can be specified on a product or machine level. For example, if you
    have one machine that only runs promo items then the constraint will
    automatically apply to all of the products that it produces.

    However, if you have a promo product that can be made by multiple machines
    then you can specify the constrain on the product level and it will
    propagate to all machines.

    If the machine is **specifically** only for promo periods, then it would be
    more efficient to set a shift pattern that applies during the run-up period
    instead of using this constraint.

    Parameters
    ----------
    start_date : str | dt.datetime | dt.date
        The start date of the production period
    end_date : str | dt.datetime | dt.date
        The end date of the production period
    product : ContinuousProduct | None, optional
        Specify a particular product that this applies to, by default None. If
        left as None, it will be determined by the context in which the
        constraint is specified (on the product-level or machine-level)
    machine : ContinuousMachine | None, optional
        Specify a particular machine that this applies to, by default None. If
        left as None, it will be determined by the context in which the
        constraint is specified (on the product-level or machine-level)
    """

    def __init__(
        self,
        start_date: str | dt.datetime | dt.date,
        end_date: str | dt.datetime | dt.date,
        product: _Product | None = None,
        machine: _Machine | None = None,
    ) -> None:
        self._id = uuid4().hex
        self.start_date = parse_datetime(start_date)
        self.end_date = parse_datetime(end_date)
        self.product = product
        self.machine = machine
        self.value = 1

    def _set_product(self, product: _Product) -> None:
        self.product = product

    def _set_machine(self, machine: _Machine) -> None:
        self.machine = machine


class ReducedProductionPeriod(HardConstraint):
    """Define a period in which the production rate is lower than normal

    **Only applies to Continous Products/Machines**

    This is useful in cases where seasonality affects production. For example,
    in a sweet factory during the summer, the higher humidity causes the batch
    rollers to slip on the sugar mixture, making them less efficient. If the
    machine drew too hard on the flow out of the rollers, it would snap the
    thread going into the cutters so they ran machines at 80% of the usual rate
    to prevent such incidents.

    Parameters
    ----------
    value : int
        A percentage of the normal run rate that applies during this period.
        For example, if a machine normally produces 100 products per minute,
        setting this as 80 would mean that the machine only produces 80
        products per minute during this period
    start_date : str | dt.datetime | dt.date
        The start date of the reduced run rate
    end_date : str | dt.datetime | dt.date
        The end date of the reduced run rate
    product : ContinuousProduct | None, optional
        Specify a particular product that this applies to, by default None. If
        left as None, it will be determined by the context in which the
        constraint is specified (on the product-level or machine-level)
    machine : ContinuousMachine | None, optional
        Specify a particular machine that this applies to, by default None. If
        left as None, it will be determined by the context in which the
        constraint is specified (on the product-level or machine-level)
    """

    def __init__(
        self,
        value: int,
        start_date: str | dt.datetime | dt.date,
        end_date: str | dt.datetime | dt.date,
        product: ContinuousProduct | None = None,
        machine: ContinuousMachine | None = None,
    ):
        self._id = uuid4().hex
        self.start_date = parse_datetime(start_date)
        self.end_date = parse_datetime(end_date)
        self.product = product
        self.machine = machine
        self.value = value

    def _set_product(self, product: ContinuousProduct) -> None:
        check_continuous_prod_only(self, product)
        self.product = product

    def _set_machine(self, machine: ContinuousMachine) -> None:
        check_continuous_machine_only(self, machine)
        self.machine = machine


class MaxStorageCapacity(HardConstraint):
    pass


class MaxProductLifetime(HardConstraint):
    pass


__all__ = ["MinProductionTime", "MaxProductionTime", "SeasonalProduction"]
