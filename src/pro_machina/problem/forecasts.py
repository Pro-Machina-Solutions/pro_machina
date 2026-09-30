from __future__ import annotations

import datetime as dt
import warnings
from decimal import Decimal
from itertools import count
from typing import TYPE_CHECKING, NewType

if TYPE_CHECKING:
    from ._constraints import HardConstraint, SoftConstraint
    from .problem import Problem
    from .products import ProdID, ProdSubtype

import numpy as np
import numpy.typing as npt

from pro_machina import options

from .._registries import UnitReg
from ..businesses import Customer
from ..costs import OrderValue
from ..durations import Duration
from ..exceptions import UnitError
from ..measures import CustomUnit, SizedDimension
from ..util import as_day_start, get_problem_buckets, parse_datetime
from .consumables import ConsID

OrderID = NewType("OrderID", int)


class Order:
    _ids = count(0)

    def __init__(
        self,
        name: str | None,
        code: str | None,
        due_date: dt.date | str,
        customer: Customer | None = None,
        order_value: OrderValue | None = None,
        lines: Orderline | list[Orderline] | None = None,
        hard_constraints: HardConstraint | list[HardConstraint] | None = None,
        soft_constraints: HardConstraint | list[HardConstraint] | None = None,
    ) -> None:
        self._id = OrderID(next(self._ids))
        if name is None and code is None:
            raise ValueError(
                "Either a name or a code must be supplied for an Order."
            )
        self.name = name
        self.code = code
        self.due_date = as_day_start(due_date)
        customer = customer
        order_value = order_value

        self._lines: dict[ProdID, Orderline] = {}
        if lines is not None:
            self.add_orderlines(lines)

        self._hard_constraints: list[HardConstraint] = []
        if hard_constraints is not None:
            self.add_hard_constraints(hard_constraints)

        self._soft_constraints: list[SoftConstraint] = []
        if soft_constraints is not None:
            self.add_soft_constraints(hard_constraints)

    def add_orderlines(self, lines: Orderline | list[Orderline]) -> None:

        if not isinstance(lines, list):
            lines = [lines]

        if not all(isinstance(line, Orderline) for line in lines):
            raise TypeError("Not a valid Orderline type.")

        for line in lines:
            if line._id in self._lines and not options["silence_warnings"]:
                _name = self.name if self.name is not None else self.code
                warnings.warn(
                    (
                        f"Orderline of {line.product.name} has been added more"
                        f" than once to order: {_name}"
                    ),
                    stacklevel=1,
                )
            self._lines[line.product._id] = line

    def add_hard_constraints(
        self, constraints: HardConstraint | list[HardConstraint]
    ) -> None:

        if not isinstance(constraints, list):
            constraints = [constraints]

        if not all(isinstance(cons, HardConstraint) for cons in constraints):
            raise TypeError("Not a valid HardConstraint type.")

        # TODO

    def add_soft_constraints(
        self, constraints: SoftConstraint | list[SoftConstraint]
    ) -> None:

        if not isinstance(constraints, list):
            constraints = [constraints]

        if not all(isinstance(cons, SoftConstraint) for cons in constraints):
            raise TypeError("Not a valid SoftConstraint type.")

        # TODO


class Orderline:
    _ids = count(0)

    def __init__(
        self, product: ProdSubtype, qty: SizedDimension | CustomUnit
    ) -> None:

        if not isinstance(product, ProdSubtype):
            raise TypeError("Not a valid Product for OrderLine")

        if not isinstance(qty, CustomUnit):
            if not product.base_dimension.is_compatible(qty):
                raise UnitError(
                    f"{qty.name()} is not in a compatible unit for"
                    f" {product.name}"
                )

        self._id = next(self._ids)
        self.product = product
        self.qty = qty


class MadeToStock:
    """Generate product demand that is not associated with a fixed order.

    Parameters
    ----------
    product : BatchProduct | ContinuousProduct
        The product that the demand relates to.
    qty : SizedDimension
        The target quantity to produce.
    start_date : str | dt.datetime
        The theoretical date that this applies to. For example, on a problem
        that starts on a Monday, you might set the start date as the following
        Friday, giving the plant five days to meet the demand.
    freq : Duration | None, optional
        The frequency with which this demand should repeat. For example,
        setting a qty of Unit(1000) and a freq of Weeks(1) will generate a
        repeating demand every seven days from the start date. Set as None for
        a one-off demand.
    end_date : str | dt.datetime | None, optional
        An optional end date for which repeated demand should cease.
    value : float | None
        The total financial value of the stock. If set to None then it will
        default to a value of 1 for each base unit. 1cm == unit == 1cm^3 etc.

    Raises
    ------
    UnitError
        Raised if the stated quantity is incompatible with the product units.
    ValueError
        Raised if an end_date is set but no freq has been specified.
    """

    def __init__(
        self,
        product: BatchProduct | ContinuousProduct,
        qty: SizedDimension,
        start_date: str | dt.datetime,
        freq: Duration | None = None,
        end_date: str | dt.datetime | None = None,
        value: float | None = None,
    ):
        self.start_date = as_day_start(start_date)

        if end_date is not None and freq is None:
            raise ValueError(
                "Cannot set an end date for MadeToStock without specifying a"
                " frequency of restocking."
            )

        if not isinstance(
            qty, CustomUnit
        ) and not product.base_dimension.is_compatible(qty):
            raise UnitError(
                f"{qty} is not a compatible quantity for {product}."
            )

        if isinstance(qty, CustomUnit):
            reg = UnitReg()
            custom_unit = reg.get_measure(qty, product)
            custom_qty = qty._tmp_qty

            self.qty: SizedDimension = product.base_dimension.get_base(
                custom_unit._base_qty * custom_qty
            )
        else:
            self.qty = qty

        self.product = product
        self.freq = freq
        if end_date is not None:
            self.end_date = parse_datetime(end_date)
        else:
            self.end_date = None  # type: ignore
        self.value = value


class DemandForecast:
    """Container class to hold all Orders and MadeToStock quantities."""

    def __init__(self) -> None:
        self._orders: list[Order] = []
        self._made_to_stock: list[MadeToStock] = []

        self._prod_demands: dict[ProdID, npt.NDArray[np.float64]] = {}
        self._cons_demands: dict[ConsID, npt.NDArray[np.float64]] = {}

        self._product_names: dict[ProdID, str] = {}

    def add_demand(self, order: Order | MadeToStock) -> None:
        """Add product demand to the forecast.

        Parameters
        ----------
        order : Order | MadeToStock
            Either a fixed-date Order or a variable MadeToStock target.
        """
        if isinstance(order, Order):
            self._orders.append(order)
        else:
            self._made_to_stock.append(order)

        self._product_names[order.product._id] = order.product.name

    def _sum_demand(
        self,
        aggregator,
        order: Order,
        _id,
        num_buckets: int,
        start_date: dt.datetime,
        horizon_secs: int,
        timebucket_secs: int,
        deflt_num_horizon_buckets: int,
        multiplier: Decimal = Decimal(1),
    ):
        # Have we seen this item before? If not, fill it out with zero base
        # demand for the whole problem
        if _id not in aggregator:
            aggregator[_id] = np.zeros(num_buckets)

        # Determine the start bucket of the order. If it comes before the start
        # date of the problem, then we need to bump it up to match
        theo_start = order.date - dt.timedelta(seconds=horizon_secs)
        if theo_start < start_date:
            theo_start = start_date
            demand_buckets = int(
                (order.date - start_date).total_seconds() / timebucket_secs
            )
            start_index = 0
            end_index = demand_buckets
        else:
            start_index = int(
                (
                    (order.date - dt.timedelta(seconds=horizon_secs))
                    - start_date
                ).total_seconds()
                / timebucket_secs
            )
            end_index = int(start_index + deflt_num_horizon_buckets)
            demand_buckets = int(deflt_num_horizon_buckets)

        demand_per_bucket = float(
            (order.qty._base_qty * multiplier) / Decimal(demand_buckets)
        )
        aggregator[_id][start_index:end_index] += demand_per_bucket

    def _process_order_list(
        self,
        order_list: list[Order],
        num_buckets: int,
        start_date: dt.datetime,
        horizon_secs: int,
        timebucket_secs: int,
        deflt_num_horizon_buckets: int,
        problem_end_date: dt.datetime,
    ):

        for order in order_list:
            if (
                order.date - dt.timedelta(seconds=horizon_secs)
                > problem_end_date
            ):
                # We don't even need to consider this because it's completely
                # outside of the problem scope
                continue

            self._sum_demand(
                aggregator=self._prod_demands,
                order=order,
                _id=order.product._id,
                num_buckets=num_buckets,
                start_date=start_date,
                horizon_secs=horizon_secs,
                timebucket_secs=timebucket_secs,
                deflt_num_horizon_buckets=deflt_num_horizon_buckets,
            )

            for subproduct_id, qty in order.product._bom_products.items():
                self._sum_demand(
                    aggregator=self._prod_demands,
                    order=order,
                    _id=subproduct_id,
                    num_buckets=num_buckets,
                    start_date=start_date,
                    horizon_secs=horizon_secs,
                    timebucket_secs=timebucket_secs,
                    deflt_num_horizon_buckets=deflt_num_horizon_buckets,
                    multiplier=qty,
                )

            for consumable_id, qty in order.product._bom_consumables.items():
                self._sum_demand(
                    aggregator=self._cons_demands,
                    order=order,
                    _id=consumable_id,
                    num_buckets=num_buckets,
                    start_date=start_date,
                    horizon_secs=horizon_secs,
                    timebucket_secs=timebucket_secs,
                    deflt_num_horizon_buckets=deflt_num_horizon_buckets,
                    multiplier=qty,
                )

    def _build(self, problem: Problem):

        num_buckets = get_problem_buckets(
            problem._start, problem._end, problem.config.timebucket
        )
        timebucket_secs = int(problem.config.timebucket.to_seconds())

        horizon_secs = int(problem.config.demand_horizon.to_seconds())
        deflt_num_horizon_buckets = int(horizon_secs / timebucket_secs)

        # First process set orders
        self._process_order_list(
            self._orders,
            num_buckets=num_buckets,
            start_date=problem._start,
            horizon_secs=horizon_secs,
            timebucket_secs=timebucket_secs,
            deflt_num_horizon_buckets=deflt_num_horizon_buckets,
            problem_end_date=problem._end,
        )

        # Now process any made to stock targets
        # The easiest way to do this is to keep raising them as fake orders
        # for the purpose of generating the demand
        mts_orders: list[Order] = []
        for mts in self._made_to_stock:
            if mts.freq is not None and mts.end_date is None:
                # Repeat up until our problem end date
                dates = [mts.start_date]
                running_date = mts.start_date
                while (
                    running_date + dt.timedelta(seconds=mts.freq.to_seconds())
                    < problem._end
                ):
                    running_date += dt.timedelta(seconds=mts.freq.to_seconds())
                    dates.append(running_date)

                for date in dates:
                    # These are for complete periods in our solver window
                    mts_orders.append(
                        Order(mts.product, date=date, qty=mts.qty)
                    )

                if running_date < problem._end:
                    # Tie up any partial period
                    partial_period = Decimal(
                        (problem._end - running_date).total_seconds()
                        / mts.freq.to_seconds()
                    )

                    mts_orders.append(
                        Order(
                            product=mts.product,
                            date=problem._end,
                            qty=mts.qty * partial_period,
                        )
                    )

            elif mts.freq is not None and mts.end_date is not None:
                # Repeat up until the specified end date or until our problem
                # end
                dates = [mts.start_date]
                running_date = mts.start_date
                while (
                    running_date + dt.timedelta(seconds=mts.freq.to_seconds())
                    < mts.end_date
                    and running_date
                    + dt.timedelta(seconds=mts.freq.to_seconds())
                    < problem._end
                ):
                    running_date += dt.timedelta(seconds=mts.freq.to_seconds())
                    dates.append(running_date)

                for date in dates:
                    # These are for complete periods in our solver window
                    mts_orders.append(
                        Order(mts.product, date=date, qty=mts.qty)
                    )

                if running_date < problem._end:
                    # Tie up any partial period. We need to know the earlier of
                    # the specified end date or the global problem end date
                    e_d = (
                        mts.end_date
                        if mts.end_date < problem._end
                        else problem._end
                    )
                    partial_period = Decimal(
                        (e_d - running_date).total_seconds()
                        / mts.freq.to_seconds()
                    )

                    mts_orders.append(
                        Order(
                            mts.product,
                            date=e_d,
                            qty=(mts.qty * partial_period),
                        )
                    )

            else:
                if mts.start_date < problem._end:
                    mts_orders.append(
                        Order(mts.product, date=mts.start_date, qty=mts.qty)
                    )
                else:
                    # We have a MTS order that is outside of the Problem
                    # window. First we need to decide whether it even exists
                    # inside the scope of the problem horizon
                    theo_start = mts.start_date - dt.timedelta(
                        seconds=horizon_secs
                    )
                    if theo_start < problem._end:
                        # At least some part of this order needs to be
                        # completed within the problem scope
                        partial_period = Decimal(
                            (problem._end - theo_start).total_seconds()
                            / horizon_secs
                        )

                        mts_orders.append(
                            Order(
                                mts.product,
                                date=problem._end,
                                qty=(mts.qty * partial_period),
                            )
                        )

        self._process_order_list(
            mts_orders,
            num_buckets=num_buckets,
            start_date=problem._start,
            horizon_secs=horizon_secs,
            timebucket_secs=timebucket_secs,
            deflt_num_horizon_buckets=deflt_num_horizon_buckets,
            problem_end_date=problem._end,
        )

        for k, v in self._prod_demands.items():
            self._prod_demands[k] = v.cumsum()

        for k, v in self._cons_demands.items():
            self._cons_demands[k] = v.cumsum()


__all__ = ["Order", "MadeToStock", "DemandForecast"]
