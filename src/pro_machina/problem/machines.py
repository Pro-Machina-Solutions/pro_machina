from __future__ import annotations

import datetime as dt
from copy import deepcopy
from itertools import count
from typing import TYPE_CHECKING, NewType, NotRequired, TypedDict

import numpy.typing as npt
import pandas as pd

if TYPE_CHECKING:
    from .problem import Problem
from warnings import warn

import numpy as np

import pro_machina

from ..durations import Duration
from ..exceptions import MachineError, ShiftDefinitionError, UnitError
from ..measures import CustomUnit, SizedDimension, _UnitRegistry
from ..util import (
    as_day_end,
    as_day_start,
    get_bucket_index,
    get_problem_buckets,
    parse_datetime,
)
from .constraints import (
    ConstraintLevel,
    HardConstraint,
    SoftConstraint,
)
from .products import (
    ContinuousProduct,
    ContinuousProductGroup,
    ProdID,
    _Product,
)
from .shifts import ShiftPattern


class _MachineProduct(TypedDict):
    product: _Product
    run_rate: NotRequired[SizedDimension | None]
    run_rate_per: NotRequired[Duration | None]


class _MachineShift(TypedDict):
    start: dt.date | None
    end: dt.date | None
    shift: ShiftPattern


MachID = NewType("MachID", int)


class _Machine:
    _ids = count()

    def __init__(self, name: str) -> None:
        self._id = MachID(next(self._ids))
        self.name = name

        self._products: dict[ProdID, _MachineProduct] = {}
        self._shifts: list[_MachineShift] = []

        self._hard_constraints: list[HardConstraint] = []
        self._soft_constraints: list[SoftConstraint] = []

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

        Raises
        ------
        ShiftDefinitionError
            An end date is set without an explicit start date
        TypeError
            Not a valid ShiftPattern passed
        ValueError
            End date is before start date
        """
        if end_date is not None and start_date is None:
            raise ShiftDefinitionError(
                "Cannot set an end date without an explicit start date"
            )

        if not isinstance(shift, ShiftPattern):
            raise TypeError("Not a valid shift pattern")

        if start_date is not None:
            start_date = parse_datetime(start_date)
        if end_date is not None:
            end_date = parse_datetime(end_date)

        if end_date is not None and start_date is not None:
            if end_date <= start_date:
                raise ValueError("End date cannot be before start date")

        self._shifts.append(
            _MachineShift(start=start_date, end=end_date, shift=shift)
        )

    def clear_shifts(self) -> None:
        """Helper function to remove any pre-defined shifts"""
        self._shifts = []

    def _build_shift_productivity(
        self, problem: Problem
    ) -> npt.NDArray[np.float64]:

        # Track total number of buckets in the problem.
        problem_num_buckets = get_problem_buckets(
            problem._start, problem._end, problem.config.timebucket
        )

        # Default all buckets to zero productivity unless no shifts are
        # specified, in which case the machine is assumed to always be on
        if not self._shifts:
            base_productivity = np.full(problem_num_buckets, 100.0)
        else:
            base_productivity = np.zeros(problem_num_buckets)

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
                pattern = shift["shift"]._yield_day(
                    date, problem.config.timebucket
                )
                start_bucket = get_bucket_index(
                    problem._start,
                    problem._end,
                    problem.config.timebucket,
                    date,
                )
                end_bucket = start_bucket + len(pattern)
                base_productivity[start_bucket:end_bucket] = pattern

        return base_productivity


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
        A unique string identifier for this machine.
    default_run_rate : SizedDimension | None, optional
        The number of units that can be produced within a certain time period.
        If this is set then it will automatically apply to all products that
        are added to the machine unless explicitly overwritten in
        `add_product()`. If specified, then the `default_per` must also be
        specified.
    default_per : Duration | None, optional
        The time frame over which the default_run_rate applies for all products
        add to the machine, unless explicityl overwritten in `add_product().
        If specified, the `default_run_rate` must also be specified.
    """

    def __init__(
        self,
        name,
        default_run_rate: SizedDimension | None = None,
        default_per: Duration | None = None,
    ) -> None:
        super().__init__(name)
        self.default_run_rate = default_run_rate
        self.default_per = default_per

    def add_product(
        self,
        product: ContinuousProduct,
        run_rate: SizedDimension | None = None,
        per: Duration | None = None,
    ) -> None:
        """Define a ContinuousProduct and its associated run rate.

        An example may be to say that the machine can make 80 units/min:
        ```
        machine = ContinuousMachine(name="Machine A")
        machine.add_product(product, run_rate=Unit(80), per=Mins(1))
        ```

        Or alternatively, 5 litres in every 15 minute period (averaged):
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
        TypeError
            Raised if something other than a ContinuousProduct is specified.
        MachineError
            Product has already been added to this machine
        MachineError
            Raised if neither the default nor the specific run rate for
            products are specified.
        UnitError
            The run rate specified for the machine is incompatible with the
            units of the product it produces e.g. Unit/Min for a product
            measured in Litres.
        """

        if not isinstance(product, ContinuousProduct):
            raise TypeError(
                f"Can only add ContinuousProduct to machine: {self.name}"
            )

        if product._id in self._products:
            raise MachineError(
                f"Product: {product.name} has already been assigned to"
                f" machine: {self.name}"
            )

        _run_rate = None
        if run_rate is not None:
            _run_rate = run_rate
        elif run_rate is None and self.default_run_rate is not None:
            _run_rate = self.default_run_rate
        else:
            raise MachineError(
                "Neither a default run rate or a specific run rate of"
                f" product has been specified for {product.name} on"
                f" {self.name}"
            )

        # Now need to check that the dimensions of the product and the run rate
        # of the machine are compatible
        if not isinstance(_run_rate, CustomUnit):
            prod_dim = product.base_dimension
            if not prod_dim.is_compatible(_run_rate):
                raise UnitError(
                    f"Production units of {type(_run_rate).__name__} for"
                    f" {self.name} are incompatible with the product unit of"
                    f" {prod_dim.__name__} for {product.name}"
                )
        else:
            reg = _UnitRegistry()
            custom_unit = reg.get_measure(_run_rate, product)
            prod_dim = product.base_dimension
            if not prod_dim.is_compatible(custom_unit):
                raise UnitError(
                    f"Production units of {_run_rate.name} for"
                    f" {self.name} are incompatible with the product unit of"
                    f" {prod_dim.__name__} for {product.name}"
                )

        _per = None
        if per is not None:
            _per = per
        elif per is None and self.default_per is not None:
            _per = self.default_per
        else:
            raise MachineError(
                "Neither a default time period or a specific time period "
                f" for the run_rate has been specified for {product.name}"
            )

        # When adding a product, we want to first "inherit" its own list of
        # constraints as a basis to ours. Make a copy such that any new
        # product changes after being added to a machine are definitely fixed.
        # At this point, no arbiter has been able to run until the machine is
        # actually added to the problem, but it will resolve product-only,
        # machine-only and machine-product pairing constraints
        self._hard_constraints.extend(deepcopy(product._hard_constraints))
        self._soft_constraints.extend(deepcopy(product._soft_constraints))

        self._products[product._id] = _MachineProduct(
            product=product,
            run_rate=_run_rate,
            run_rate_per=_per,
        )

    def add_product_group(
        self,
        group: ContinuousProductGroup,
        run_rates: list[tuple[(str, SizedDimension, Duration)]] | None = None,
    ):
        """Add all products within a ProductGroup to a machine.

        If the default run rate for the machine is specified then it will be
        applied to all products within the group. Additionally, all individual
        constraints for each product (on the Product level) in the group will
        be transferred over, similar to `add_product()`.

        However, if you wish to add all of the products and their constraints,
        but specify individual run rates for each of the products then these
        must be specified seperately. For example:

        ```python3
        prod_1 = ContinuousProduct("Prod 1", base_dimension=BaseUnit)

        # Apply a constraint to just one of the products before adding to the
        # group
        prod_2 = ContinuousProduct("Prod 2", base_dimension=BaseUnit)
        prod_2.add_hard(MaxProductionTime(Hours(24)))

        prod_3 = ContinuousProduct("Prod 3", base_dimension=BaseUnit)

        group = ContinuousProductGroup("Sweets", [prod_1, prod_2, prod_3])
        # Add a constraint to all of the products in the group
        group.add_hard_constraint(MinProductionTime(Hours(2)))

        mach_1 = ContinuousMachine(
            "Machine 1", default_run_rate=Unit(50), default_per=Mins(1)
        )

        # This will copy all of the products over to the machine with the
        # default run rate of the machine. The group-level constraint will be
        # copied over for all of the products, in addition to individual
        # MaxProductionTime for prod_2 and the MinProductionTime for all
        # products.
        mach_1.add_product_group(group)

        # However, if we want to specify the individual run rates, but keep the
        # behaviour of the constraints the same, use:

        mach_1.add_product_group(
            group=group,
            run_rates=[
                ("Prod 1", Unit(45), Mins(1)),
                ("Prod 2", Unit(52), Mins(1)),
                ("Prod 3", Unit(50), Mins(1))
            ]
        )
        # Note that the run rate must be specified for all products, even
        # though prod_3 is actually running at the same rate as the machine
        # default.
        ```

        Parameters
        ----------
        group : ContinuousProductGroup
            A ContinuousProductGroup containing multiple products to be added
            to the machine.
        run_rates : list[tuple[, optional
            An optional list of tuples describing the individual run rates of
            each product within the group, by default None. If given, the rate
            must be specified for all products, regardless of whether the rate
            is the same as the machine default.

        Raises
        ------
        TypeError
            Something other than a ContinuousProductGroup was added.
        ValueError
            Product name not recognised for run rate specification.
        MachineError
            No product run rate has been specified.
        MachineError
            Custom product run rate definitions do not cover all products in
            the ContinuousProductGroup.
        MachineError
            A product has already been added to the machine.
        """

        if not isinstance(group, ContinuousProductGroup):
            raise TypeError("Not a valid ContinuousProductGroup.")

        if run_rates is None and (
            self.default_per is None or self.default_run_rate is None
        ):
            raise MachineError(
                "Neither a default nor specific run rate is specified for the"
                " product group."
            )

        if run_rates is not None:
            if len(run_rates) != len(group._products):
                raise MachineError(
                    "If providing custom run rates for each product in a"
                    " ProductGroup, they either must all be specified or"
                    " completely omitted to take the machine defaults."
                )

            for prod_name, run_rate, per in run_rates:
                prod = group._product_by_name[prod_name]
                self.add_product(prod, run_rate=run_rate, per=per)

        else:
            for prod in group._products.values():
                self.add_product(prod)

    def add_hard_constraint(
        self,
        constraints: HardConstraint | list[HardConstraint],
        _level: int = ConstraintLevel.MACHINE.value,
    ) -> None:

        if isinstance(constraints, HardConstraint):
            constraints = [constraints]

        if not all(isinstance(item, HardConstraint) for item in constraints):
            raise TypeError("Constraints must all be of type HardConstraint.")

        for constraint in constraints:
            if constraint.machine is None:
                constraint._set_machine(self)
            constraint._level = _level

        self._hard_constraints.extend(constraints)


class ContinuousMachineGroup:
    _ids = count(0)

    def __init__(
        self, name: str, machines: list[ContinuousMachine] | None = None
    ) -> None:
        self._id = MachID(next(self._ids))
        self.name = name
        self.machines: list[ContinuousMachine] = (
            machines if machines is not None else []
        )

        if self.machines:
            if not all(
                isinstance(item, ContinuousMachine) for item in self.machines
            ):
                raise TypeError("Incorrect type added to machine group.")

        self._hard_constraints: list[HardConstraint] = []
        self._soft_constraints: list[SoftConstraint] = []

    def add_machine(
        self, machines: ContinuousMachine | list[ContinuousMachine]
    ) -> None:
        """Add a machine to an existing grouping.

        Parameters
        ----------
        machines : _Machine | list[_Machine]
            The machine(s) to be added.

        Raises
        ------
        TypeError
            Attempted to add something other than a Machine to the grouping.
        """
        if isinstance(machines, _Machine):
            self.machines.append(machines)
        else:
            self.machines.extend(machines)

        prev_len = len(self.machines)
        self.machines = list(set(self.machines))
        if (
            len(self.machines) < prev_len
            and not pro_machina.options["silence_warnings"]
        ):
            warn(
                f"\n Duplicate machines were added to group: {self.name}",
                stacklevel=1,
            )

        if not all(isinstance(item, _Machine) for item in self.machines):
            raise TypeError("Incorrect type added to machine group")


class BatchMachine(_Machine):
    def __init__(self, name) -> None:
        super().__init__(name)

        self._products: dict[ProdID, _MachineProduct] = {}

    # def add_product(self, product: BatchProduct):

    #     if not isinstance(product, BatchProduct):
    #         raise MachineError("Can only add BatchProduct to this machine")

    #     self._products[product._id] = _MachineProduct(
    #         product=product,
    #         hard_constraints=product._hard_constraints,
    #         soft_constraints=product._soft_constraints,
    #     )
