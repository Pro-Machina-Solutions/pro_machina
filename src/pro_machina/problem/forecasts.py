from __future__ import annotations

import datetime as dt
import warnings
from decimal import Decimal
from itertools import count
from typing import TYPE_CHECKING, Any, NewType, TypedDict

from .products import ProdID, ProdSubtype, ProductGroup

if TYPE_CHECKING:
    from ._constraints import HardConstraint, SoftConstraint
    from .problem import Problem

import numpy as np
import numpy.typing as npt

from pro_machina import options

from .._registries import ProductReg
from ..businesses import Customer
from ..costs import OrderValue
from ..durations import Duration
from ..measures import Quantity, resolve_qty
from ..util import (
    as_day_start,
    get_bucket_index,
    get_problem_buckets,
)
from .consumables import ConsID

OrderID = NewType("OrderID", int)
MtsID = NewType("MtsID", int)


class Order:
    _ids = count(0)

    def __init__(
        self,
        due_date: dt.date | str,
        name: str | None = None,
        code: str | None = None,
        production_lead_time: Duration | None = None,
        customer: Customer | None = None,
        order_value: OrderValue | None = None,
        lines: Orderline | list[Orderline] | None = None,
        hard_constraints: HardConstraint | list[HardConstraint] | None = None,
        soft_constraints: SoftConstraint | list[SoftConstraint] | None = None,
    ) -> None:
        self._id = OrderID(next(self._ids))
        if name is None and code is None:
            raise ValueError(
                "Either a name or a code must be supplied for an Order."
            )
        self.name = name
        self.code = code
        self.due_date = as_day_start(due_date)
        self.production_lead_time = (
            production_lead_time if production_lead_time is not None else None
        )

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
            self.add_soft_constraints(soft_constraints)

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

    def __init__(self, product: ProdSubtype, qty: Quantity) -> None:

        self._id = next(self._ids)
        self.product = product
        self.qty = resolve_qty(qty, product)


class MadeToStock:
    _ids = count(0)

    def __init__(
        self,
        product: ProdSubtype | ProductGroup,
        qty: Quantity,
        start_date: str | dt.datetime,
        end_date: str | dt.datetime | None = None,
        freq: Duration | None = None,
        hard_constraints: HardConstraint | list[HardConstraint] | None = None,
        soft_constraints: SoftConstraint | list[SoftConstraint] | None = None,
    ):
        self._id = MtsID(next(self._ids))

        if not isinstance(product, (ProductGroup, ProdSubtype)):
            raise TypeError("Not a valid Product or Product group for MTS.")

        self.start_date = as_day_start(start_date)
        if freq is None and end_date is None:
            raise ValueError(
                "Either a frequency or an end date must be specified for"
                " MadeToStock"
            )

        self.end_date = (
            as_day_start(end_date) if end_date is not None else None
        )

        # Validate now - raises if qty isn't a measure, is incompatible, or
        # is a CustomUnit not sized for every product - but keep it
        # unresolved: for a ProductGroup it means a different amount per
        # product.
        members = (
            product._products.values()
            if isinstance(product, ProductGroup)
            else [product]
        )
        for member in members:
            resolve_qty(qty, member)

        self.qty = qty
        self.product = product
        self.freq = freq

        self._hard_constraints: list[HardConstraint] = []
        if hard_constraints is not None:
            self.add_hard_constraints(hard_constraints)

        self._soft_constraints: list[SoftConstraint] = []
        if soft_constraints is not None:
            self.add_soft_constraints(soft_constraints)

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


class _MTSCycle(TypedDict):
    start_index: int
    end_index: int
    proportion: Decimal


class DemandForecast:
    def __init__(
        self,
        orders: Order | list[Order] | None = None,
        mts: MadeToStock | list[MadeToStock] | None = None,
    ) -> None:
        self.orders: list[Order] = []
        self._seen_orders: set[OrderID] = set()
        self.mts: list[MadeToStock] = []
        self._seen_mts: set[MtsID] = set()
        self._seen_mts_products: set[ProdID] = set()

        if orders is not None:
            self.add_order(orders)
        if mts is not None:
            self.add_mts(mts)

        # Containers to be populated at problem build time
        self._prod_demand_buckets: dict[ProdID, npt.NDArray[np.float64]] = {}
        self._cons_demand_buckets: dict[ConsID, npt.NDArray[np.float64]] = {}

    def add_order(self, orders: Order | list[Order]) -> None:

        if isinstance(orders, Order):
            orders = [orders]

        if not all(isinstance(order, Order) for order in orders):
            raise TypeError("Invalid Order type passed.")

        for order in orders:
            if order._id in self._seen_orders:
                _name = order.name if order.name is not None else order.code
                raise ValueError(f"Cannot add the same order: {_name} twice.")
            self.orders.append(order)

    def add_mts(self, mts: MadeToStock | list[MadeToStock]) -> None:

        if isinstance(mts, MadeToStock):
            mts = [mts]

        if not all(isinstance(m, MadeToStock) for m in mts):
            raise TypeError("Invalid MadeToStock type passed.")

        for m in mts:
            if m._id in self._seen_mts:
                raise ValueError("Cannot raise this MTS order twice")

            if isinstance(m.product, ProdSubtype):
                if m.product._id in self._seen_mts_products:
                    raise ValueError(
                        f"Cannot make a second MTS order for {m.product.name}"
                    )

            elif isinstance(m.product, ProductGroup):
                for prod in m.product._products.values():
                    if prod._id in self._seen_mts_products:
                        raise ValueError(
                            f"Cannot make a second MTS order for {prod.name}"
                        )

            self.mts.append(m)

    def _preprocessing(self, problem: Problem) -> None:
        self.problem = problem
        self.prob_start = problem._start
        self.prob_end = problem._end
        self.timebucket = problem.config.timebucket

        self.num_buckets = get_problem_buckets(
            self.prob_start, self.prob_end, self.timebucket
        )
        self.dflt_demand_horizon_secs = (
            problem.config.demand_horizon.to_seconds()
        )

        self.null_demand = np.zeros(shape=self.num_buckets, dtype=np.float64)

    def _process_order_buckets(
        self, order: Order, prod_reg: ProductReg
    ) -> dict[str, Any] | None:

        if order.production_lead_time is not None:
            raw_prod_start_date = order.due_date - dt.timedelta(
                seconds=order.production_lead_time.to_seconds()
            )
        else:
            raw_prod_start_date = order.due_date - dt.timedelta(
                seconds=self.dflt_demand_horizon_secs
            )

        if (raw_prod_start_date > self.prob_end) or (
            order.due_date < self.prob_start
        ):
            # Order isn't even in our problem time period, including its ramp
            # up time. Just ignore it.
            return None

        # Bump dates to be bounded by our problem start and end (if necessary)
        prod_start_date = max(self.prob_start, raw_prod_start_date)
        prod_end_date = min(self.prob_end, order.due_date)

        total_order_buckets = int(
            (order.due_date - raw_prod_start_date).total_seconds()
            / self.timebucket.to_seconds()
        )

        if prod_start_date == self.prob_start:
            start_bucket_index = 0
        else:
            start_bucket_index = get_bucket_index(
                self.problem,
                prod_start_date,
            )

        if prod_end_date == self.prob_end:
            end_bucket_index = total_order_buckets
        else:
            end_bucket_index = get_bucket_index(self.problem, prod_end_date)

        prod_demand: dict[ProdID, Decimal] = {}
        cons_demand: dict[ConsID, Decimal] = {}

        for prod_id, line in order._lines.items():
            _prod = prod_reg.get_by_id(prod_id)
            base_qty_per_bucket = line.qty._base_qty / total_order_buckets
            prod_demand[prod_id] = base_qty_per_bucket

            # Account for any subproducts
            for subprod_id, demand in _prod._bom_products.items():
                prod_demand[subprod_id] = prod_demand.get(subprod_id, 0) + (
                    base_qty_per_bucket * demand
                )

            # Now account for consumables
            for cons_id, demand in _prod._bom_consumables.items():
                cons_demand[cons_id] = cons_demand.get(cons_id, 0) + (
                    base_qty_per_bucket * demand
                )

        return {
            "start_index": start_bucket_index,
            "end_index": end_bucket_index,
            "product_demands": prod_demand,
            "consumable_demands": cons_demand,
        }

    def _process_orders(self) -> None:
        prod_reg = ProductReg()

        for order in self.orders:
            res = self._process_order_buckets(order=order, prod_reg=prod_reg)
            if res is None:
                continue
            for prod_id, demand in res["product_demands"].items():
                if prod_id not in self._prod_demand_buckets:
                    base = self.null_demand.copy()
                    base[res["start_index"] : res["end_index"]] = demand
                    self._prod_demand_buckets[prod_id] = base
                else:
                    self._prod_demand_buckets[prod_id][
                        res["start_index"] : res["end_index"]
                    ] += float(demand)

            for cons_id, demand in res["consumable_demands"].items():
                if cons_id not in self._cons_demand_buckets:
                    base = self.null_demand.copy()
                    base[res["start_index"] : res["end_index"]] = demand
                    self._cons_demand_buckets[cons_id] = base
                else:
                    self._cons_demand_buckets[cons_id][
                        res["start_index"] : res["end_index"]
                    ] += float(demand)

    def _decipher_mts_cycle(self, mts: MadeToStock) -> list[_MTSCycle] | None:

        # First just kick out any redundant cycles
        if mts.start_date > self.prob_end:
            # Starts after the end of our window of intered
            return None

        if mts.end_date is not None and mts.end_date < self.prob_start:
            # Ended before our window of interest
            return None

        if mts.end_date is None:
            # This is a theoretical value. For example, we might have an MTS on
            # a Weeks(2) cycle and the problem end date lands in the middle of
            # that period. We will need to make up part of that stock
            end_date = self.prob_end
        else:
            end_date = mts.end_date

        # cycle_seconds = mts.freq.to_seconds()
        # cycle_buckets = int(cycle_seconds / self.timebucket.to_seconds())
        cycle_demands: list[_MTSCycle] = []

        if mts.freq is None:
            # This is a one-off production run. How much of the makespan falls
            # within the problem span itself?

            # This should be caught separately in constructor of MadeToStock
            assert mts.end_date is not None

            total_mts_makespan = (
                mts.end_date - mts.start_date
            ).total_seconds()

            total_prob_makespan = (
                min(mts.end_date, self.prob_end)
                - max(mts.start_date, self.prob_start)
            ).total_seconds()

            # Use min() just in case there are rounding errors. Mathematically
            # not necessary
            proportion = min(1.0, total_prob_makespan / total_mts_makespan)

            cycle_demands.append(
                _MTSCycle(
                    start_index=get_bucket_index(
                        self.problem, max(self.prob_start, mts.start_date)
                    ),
                    end_index=get_bucket_index(
                        self.problem, min(self.prob_end, end_date)
                    ),
                    proportion=Decimal(proportion),
                )
            )
            return cycle_demands

        # Now we have to handle actual recurring frequency, which needs
        # resolving on both ends; start date and end date
        cycle_seconds = mts.freq.to_seconds()
        rolling_date = self.prob_start

        if mts.start_date < self.prob_start:
            # There could be N completed cycles beforehand but we're only
            # interested in how far we are into the cycle that crosses the
            # prob_start threshold. So, we need a multiplier to scale down
            # the first cycle demand.

            total_start_discrep_secs = (
                self.prob_start - mts.start_date
            ).total_seconds()

            part_cycle_secs = total_start_discrep_secs % cycle_seconds
            remaining_cycle_secs = cycle_seconds - part_cycle_secs

            cycle_demands.append(
                _MTSCycle(
                    start_index=get_bucket_index(
                        self.problem, self.prob_start
                    ),
                    end_index=get_bucket_index(
                        self.problem,
                        self.prob_start
                        + dt.timedelta(seconds=remaining_cycle_secs),
                    ),
                    proportion=Decimal(remaining_cycle_secs / cycle_seconds),
                )
            )
            rolling_date = self.prob_start + dt.timedelta(
                seconds=remaining_cycle_secs
            )

        elif (mts.start_date == self.prob_start) and (
            mts.start_date + dt.timedelta(seconds=cycle_seconds)
            < self.prob_end
        ):
            # In this case, we have just shifted the first MTS target because
            # it's the same as the start date. Our first demand is therefore
            # realised at the end of the first cycle.
            end = mts.start_date + dt.timedelta(seconds=cycle_seconds)
            cycle_demands.append(
                _MTSCycle(
                    start_index=get_bucket_index(
                        self.problem, self.prob_start
                    ),
                    end_index=get_bucket_index(self.problem, end),
                    proportion=Decimal("1.0"),
                )
            )
            rolling_date = end

        elif (mts.start_date >= self.prob_start) and (
            mts.start_date + dt.timedelta(seconds=cycle_seconds) >= end_date
        ):
            tot_cycle = (end_date - mts.start_date).total_seconds()
            in_cycle = (
                min(self.prob_end, end_date)
                - max(self.prob_start, mts.start_date)
            ).total_seconds()
            proportion = min(1.0, in_cycle / tot_cycle)

            cycle_demands.append(
                _MTSCycle(
                    start_index=get_bucket_index(self.problem, mts.start_date),
                    end_index=get_bucket_index(self.problem, self.prob_end),
                    proportion=Decimal(proportion),
                )
            )
            # We're done here; can't be another cycle
            return cycle_demands
        else:
            while (
                rolling_date + dt.timedelta(seconds=cycle_seconds) <= end_date
            ):
                cycle_end = rolling_date + dt.timedelta(seconds=cycle_seconds)
                cycle_demands.append(
                    _MTSCycle(
                        start_index=get_bucket_index(
                            self.problem, rolling_date
                        ),
                        end_index=get_bucket_index(self.problem, cycle_end),
                        proportion=Decimal("1.0"),
                    )
                )
                rolling_date = cycle_end

        # Now see if we need to tie up the end period in case it's a partial
        # cycle
        if rolling_date < end_date:
            missing_prop = (
                rolling_date + dt.timedelta(seconds=cycle_seconds) - end_date
            ).total_seconds() / cycle_seconds
            cycle_demands.append(
                _MTSCycle(
                    start_index=get_bucket_index(self.problem, rolling_date),
                    end_index=get_bucket_index(self.problem, end_date),
                    proportion=Decimal(missing_prop),
                )
            )

        return cycle_demands

    def _process_mts(self) -> None:
        prod_reg = ProductReg()

        for mts in self.mts:
            # First we need to resolve the units for all products in MTS
            resolved_qtys: dict[ProdID, Decimal] = {}

            if isinstance(mts.product, ProdSubtype):
                tot_demand = resolve_qty(mts.qty, mts.product)._base_qty
                resolved_qtys[mts.product._id] = tot_demand
            else:
                # Need to cycle through all products in group
                for product in mts.product._products.values():
                    tot_demand = resolve_qty(mts.qty, product)._base_qty
                    resolved_qtys[product._id] = tot_demand

            # Now go through the individual cycles
            cycles = self._decipher_mts_cycle(mts)

            if cycles is None:
                # Outside of problem date range
                continue

            for cycle in cycles:
                for prod_id, tot_demand in resolved_qtys.items():
                    problem_demand = tot_demand * cycle["proportion"]
                    buckets = cycle["end_index"] - cycle["start_index"]
                    per_bucket = problem_demand / buckets
                    if prod_id not in self._prod_demand_buckets:
                        self._prod_demand_buckets[prod_id] = (
                            self.null_demand.copy()
                        )

                    self._prod_demand_buckets[prod_id][
                        cycle["start_index"] : cycle["end_index"]
                    ] += float(per_bucket)

                    _prod = prod_reg.get_by_id(prod_id)

                    # Account for any subproducts
                    for subprod_id, demand in _prod._bom_products.items():
                        if subprod_id not in self._prod_demand_buckets:
                            self._prod_demand_buckets[subprod_id] = (
                                self.null_demand.copy()
                            )
                        self._prod_demand_buckets[subprod_id][
                            cycle["start_index"] : cycle["end_index"]
                        ] = float(per_bucket * demand)

                    # Now account for consumables
                    for cons_id, demand in _prod._bom_consumables.items():
                        if cons_id not in self._cons_demand_buckets:
                            self._cons_demand_buckets[cons_id] = (
                                self.null_demand.copy()
                            )
                        self._cons_demand_buckets[cons_id][
                            cycle["start_index"] : cycle["end_index"]
                        ] += float(per_bucket * demand)

    def _build(self, problem: Problem) -> None:
        self._preprocessing(problem)
        self._process_orders()
        self._process_mts()


__all__ = ["DemandForecast", "MadeToStock", "Order", "Orderline"]
