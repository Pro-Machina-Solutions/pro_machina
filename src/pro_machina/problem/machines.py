from __future__ import annotations

import datetime as dt
from collections.abc import Sequence
from itertools import count
from typing import TYPE_CHECKING, NotRequired, TypedDict

import pandas as pd

if TYPE_CHECKING:
    from .problem import Problem
from warnings import warn

import numpy as np

import pro_machina

from ..durations import Days, Duration
from ..exceptions import MachineError, ShiftDefinitionError
from ..measures import SizedDimension
from ..util import (
    as_day_end,
    as_day_start,
    get_problem_buckets,
    to_str_date,
)
from .constraints import Constraint, HardConstraint, SoftConstraint
from .products import BatchProduct, ContinuousProduct, _Product
from .shifts import ShiftPattern


class _MachineProduct(TypedDict):
    product: _Product
    hard_constraints: list[HardConstraint]
    soft_constraints: list[SoftConstraint]
    run_rate: NotRequired[SizedDimension]
    run_rate_per: NotRequired[Duration]


class _MachineShift(TypedDict):
    start: str | None
    end: str | None
    shift: ShiftPattern


class _Machine:
    _ids = count(0)

    def __init__(self, name: str) -> None:
        self._id = next(self._ids)
        self.name = name

        self._products: dict[int, _MachineProduct] = {}
        self._shifts: list[_MachineShift] = []

    def add_shift(
        self,
        shift: ShiftPattern,
        start_date: str | dt.datetime | None = None,
        end_date: str | dt.datetime | None = None,
    ) -> None:
        """Add a shift rotation to a machine

        If a shift is specified without a start and end date, it will be
        assumed that the machine operates on this shift pattern throughout the
        span of the problem.

        It's important to note that shifts are processed in order. Therefore,
        if you specify a 6-2 shift pattern with no dates first, that will be
        the assumed base shift. If you then specify a 6-2,2-10 shift for a
        couple of weeks, that will take precedence over the regular 6-2 shift
        for those two weeks. However, if you specify the shifts the other way
        around, the 6-2,2-10 shift rotation will be completely overwritten.

        Parameters
        ----------
        shift : ShiftPattern
            A defined shift pattern for a model time period
        start_date : str | dt.datetime | None, optional
            The start date of the particular shift rotation
        end_date : str | dt.datetime | None, optional
            The end date of the particular shift rotation
        """
        if end_date is not None and start_date is None:
            raise ShiftDefinitionError(
                "Cannot set an end date without an explicit start date"
            )

        if not isinstance(shift, ShiftPattern):
            raise TypeError("Not a valid shift pattern")

        if start_date is not None:
            start_date = to_str_date(start_date)
        if end_date is not None:
            end_date = to_str_date(end_date)

        if end_date is not None and start_date is not None:
            if end_date < start_date:
                raise ValueError("End date cannot be before start date")

        self._shifts.append(
            _MachineShift(start=start_date, end=end_date, shift=shift)
        )

    def clear_shifts(self) -> None:
        """Helper function to remove any pre-defined shifts"""
        self._shifts = []

    def _build_shift_productivity(self, problem: Problem):
        # Track total number of buckets in the problem.
        prob_num_buckets = get_problem_buckets(problem)

        # Default all buckets to zero productivity
        base_array = np.zeros(prob_num_buckets)

        # Shift patterns can only be applied on a per-day basis. Therefore, get
        # the daily number of buckets too. We can just keep iterating through
        # and adding a day each time to fill out our base array
        num_daily_buckets = int(
            Days(1).to_seconds() / problem.config._timebucket.to_seconds()
        )
        bucket_tally = 0

        for shift in self._shifts:
            if shift["start"] is None:
                start_date = problem._start
            else:
                start_date = as_day_start(shift["start"])
            if shift["end"] is None:
                end_date = problem._end
            else:
                end_date = as_day_end(shift["end"])

            dates = pd.date_range(
                start_date, end_date, freq="1D", inclusive="left"
            )
            for date in dates:
                print("Yielding", date)
                a = shift["shift"]._yield_day(date, problem.config.timebucket)
                print(a)


class ContinuousMachine(_Machine):
    """Create a machine that manufactures products in variable-length runs.

    Unlike most machines in a Job Shop scheduling problem, a ContinuousMachine
    can make products in variable-length runs. All of the products that it
    makes must also be of ContinuousProduct type. This means that the machine
    could (in some hypothetical solution for one shift rotation) run:
    - 06:00-11:30: Product A at X/min
    - 11:30-12:00: Switchover from Product A to Product B
    - 12:00-13:00: Product B at Y/min
    - 13:00-13:30: Downtime for a break
    - 13:30-14:00: product B at Y/min
    - 14:00-: Whatever rolls over onto the next shift (or shutdown)

    A combination of constraints can direct this specific behaviour, such as
    customised switchover times between products, minimum/maximum duration
    production runs and many more. The main point, though, is that the length
    of production runs is not strictly set for each block of production and
    can therefore scale in order to best meet demand for each product.

    Parameters
    ----------
    name : str
        The name of the machine. It does not have to be unique.
    """

    def __init__(self, name) -> None:
        super().__init__(name)

    def add_product(
        self,
        product: ContinuousProduct,
        run_rate: SizedDimension,
        per: Duration,
    ) -> None:
        """Define a ContinuousProduct and its associated run rate.

        An example may be to say that the machine can make 80 units/min:
        ```
        machine = ContinuousMachine(name="Machine A")
        machine.add_product(product, run_rate=Unit(80), per=Mins(1))
        ```

        Or alternatively, 5 litres (averaged) in every 15 minute period:
        ```
        machine = ContinuousMachine(name="Machine A")
        machine.add_product(product, run_rate=Litre(5), per=Mins(15))
        ```

        Parameters
        ----------
        product : ContinuousProduct
            Specify the product that this machine can make.
        run_rate : SizedDimension
            A dimension describing the output of this machine.
        per : Duration
            The time period over which the run_rate applies.

        Raises
        ------
        MachineError
            Raised if something other than a ContinuousProduct is specified.
        """

        if not isinstance(product, ContinuousProduct):
            raise MachineError(
                f"Can only add ContinuousProduct to machine: {self.name}"
            )

        # Copy over the constraints at this point. They may get overwritten
        # using `add_product_constraint` and we don't want that to affect the
        # product itself for other machines
        self._products[product._id] = _MachineProduct(
            product=product,
            hard_constraints=product._hard_constraints[:],
            soft_constraints=product._soft_constraints[:],
            run_rate=run_rate,
            run_rate_per=per,
        )

    def add_product_constraint(
        self,
        product: ContinuousProduct,
        constraint: HardConstraint | SoftConstraint,
    ) -> None:
        """Define a constraint on the **machine** level for this product.

        The method takes both Hard and Soft-constraints along with the specific
        product that it applies to for this specific machine. The machine-level
        constraint will automatically supersede any duplicate constraint that
        had been defined on the **product** level.

        For example, one could set a `MaxProductionTime` hard constraint on the
        **product** level that will apply to all machines by default:

        ```
        from pro_machina import ContinuousMachine, ContinuousProduct
        from pro_machina.durations import Hours
        from pro_machina.problem.constraint import MaxProductionTime

        product = ContinuousProduct("Prod A")
        product.add_hard_constraint(MaxProductionTime(Hours(8)))

        machine = ContinuousMachine("Machine 1")
        # The product-level constraint is automatically carried over
        machine.add_product(product, run_rate=Unit(80), per=Mins(1))
        ```

        That is useful if all machines run under the same circumstances, but
        you can override that for a specific machine by re-defining it using
        this method:

        ```
        from pro_machina import ContinuousMachine, ContinuousProduct
        from pro_machina.durations import Hours, Mins
        from pro_machina.measures import BaseUnit, Unit
        from pro_machina.problem.constraints import MaxProductionTime

        product = ContinuousProduct("Prod A", BaseUnit)
        # Set the default constraint on the product level for all machines
        product.add_hard_constraint(MaxProductionTime(Hours(8)))

        for x in range(10):
            if x == 5:
                # Special-case the constraint for this product-machine combo
                machine = ContinuousMachine(f"Machine {x}")
                machine.add_product(product, run_rate=Unit(80), per=Mins(1))
                machine.add_product_constraint(
                    product,
                    MaxProductionTime(Hours(4))
                )
            else:
                # Get the default MaxProductionTime: 8hrs
                machine = ContinuousMachine(f"Machine {x}")
                machine.add_product(product, run_rate=Unit(80), per=Mins(1))
        ```

        The code will issue a warning for every constraint overwritten in this
        way. To stop these warnings, you can set `config.silence_warnings =
        True`

        Parameters
        ----------
        product : ContinuousProduct
            Specify the product that this constraint applies to for this
            specific machine.
        constraint : HardConstraint | SoftConstraint
            Constraint to be added. If the constraint already exists on the
            product level, it will be overwritten for this specific machine.

        Raises
        ------
        MachineError
            Raised if this product has not already been specified as something
            this machine can produce.
        """
        if product._id not in self._products:
            raise MachineError(
                f"Product: {product.name} has not been added to {self.name}"
            )

        _product = self._products[product._id]

        existing_cons: Sequence[Constraint]

        if isinstance(constraint, HardConstraint):
            existing_cons = _product["hard_constraints"]
        else:
            existing_cons = _product["soft_constraints"]

        if constraint in existing_cons:
            if pro_machina.options["silence_warnings"]:
                warn(
                    "\n"
                    + (
                        f"{constraint.__class__.__name__} has already"
                        f" been defined for {product.name} and is being"
                        f" overwritten by {constraint} for Machine:"
                        f" {self.name}"
                    ).lstrip(),
                    stacklevel=2,
                )
            existing_cons = [con for con in existing_cons if con != constraint]
            existing_cons.append(constraint)  # type: ignore
        else:
            existing_cons.append(constraint)  # type: ignore

        if isinstance(constraint, HardConstraint):
            _product["hard_constraints"] = existing_cons  # type: ignore
        else:
            _product["soft_constraints"] = existing_cons  # type: ignore


class BatchMachine(_Machine):
    def __init__(self, name) -> None:
        super().__init__(name)

        self._products: dict[int, _MachineProduct] = {}

    def add_product(self, product: BatchProduct):

        if not isinstance(product, BatchProduct):
            raise MachineError("Can only add BatchProduct to this machine")

        self._products[product._id] = _MachineProduct(
            product=product,
            hard_constraints=product._hard_constraints,
            soft_constraints=product._soft_constraints,
        )
