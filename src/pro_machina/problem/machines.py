from __future__ import annotations

import datetime as dt
from copy import deepcopy
from itertools import count
from typing import TYPE_CHECKING, Any, NewType, NotRequired, TypedDict

import numpy.typing as npt
import pandas as pd

if TYPE_CHECKING:
    from ..locations import Department, Factory
    from .problem import Problem

import numpy as np

from .._registries import UnitReg
from ..durations import Duration
from ..exceptions import MachineError, ShiftDefinitionError, UnitError
from ..measures import CustomUnit, SizedDimension
from ..util import (
    as_day_end,
    as_day_start,
    get_bucket_index,
    get_problem_buckets,
    parse_datetime,
)
from ._constraints import (
    ConstraintLevel,
    HardConstraint,
    SoftConstraint,
)
from .products import (
    ContinuousProduct,
    ProdID,
    ProductGroup,
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
MachName = NewType("MachName", str)
MachGroupID = NewType("MachGroupID", int)
MachGroupName = NewType("MachGroupName", str)


class _Machine:
    _ids = count()

    def __init__(self, name: str) -> None:
        self._id = MachID(next(self._ids))
        self.name = MachName(name)

        self._products: dict[ProdID, _MachineProduct] = {}
        self._product_ids: set[ProdID] = set()
        self._shifts: list[_MachineShift] = []

        self._hard_constraints: list[HardConstraint] = []
        self._soft_constraints: list[SoftConstraint] = []

        self._department: Department | None = None
        self._factory: Factory | None = None

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
        name: str,
        default_run_rate: SizedDimension | None = None,
        default_per: Duration | None = None,
    ) -> None:
        super().__init__(name=name)
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

        if product._id in self._product_ids:
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
            reg = UnitReg()
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
        self._product_ids.add(product._id)

    def add_product_group(
        self,
        group: ProductGroup,
        run_rates: list[dict[str, Any]] | None = None,
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
        # Note that prod_1 has a specified product code. The others do not.
        prod_1 = ContinuousProduct(
            name="Prod 1",
            code="1234",
            base_dimension=BaseUnit
        )

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
                {
                    "prod_name": "Prod 1",
                    "prod_code": "1234",
                    "run_rate": Unit(45),
                    "per": Mins(1)
                },
                {"prod_name": "Prod 2", "run_rate": Unit(50), "per": Mins(1)},
                {"prod_name": "Prod 3", "run_rate": Unit(52), "per": Mins(1)},
            ]
        )
        # Note that the run rate must be specified for all products, even
        # though prod_3 is actually running at the same rate as the machine
        # default. Also note that, if the product does not have an associated
        # product code, the "prod_code" field can be omitted for brevity.
        ```

        Parameters
        ----------
        group : ProductGroup
            A ProductGroup containing multiple ContinuousProduct to be added
            to the machine.
        run_rates : list[dict[str, Any], optional
            An optional list of tuples describing the individual run rates of
            each product within the group, by default None. If given, the rate
            must be specified for all products, regardless of whether the rate
            is the same as the machine default.

        Raises
        ------
        TypeError
            Something other than a ProductGroup was added.
        TypeError
            The ProductGroup does not consist of ContinuousProduct instances.
        MachineError
            No product run rate has been specified.
        MachineError
            Custom product run rate definitions do not cover all products in
            the ContinuousProductGroup.
        MachineError
            A product has already been added to the machine.
        """

        if not isinstance(group, ProductGroup):
            raise TypeError("Not a valid ProductGroup.")

        if not all(
            isinstance(prod, ContinuousProduct)
            for prod in group._products.values()
        ):
            raise TypeError("Attempted to add a BatchProduct group.")

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

            for entry in run_rates:
                code = entry.get("prod_code")
                prod = group.get_prod_by_name(
                    product_name=entry["prod_name"], product_code=code
                )
                assert isinstance(prod, ContinuousProduct)
                self.add_product(
                    prod, run_rate=entry["run_rate"], per=entry["per"]
                )

        else:
            for prod in group._products.values():
                assert isinstance(prod, ContinuousProduct)
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


class MachineGroup:
    _ids = count(0)

    def __init__(
        self,
        group_name: str,
        machines: MachineSubtype | list[MachineSubtype] | None = None,
    ) -> None:
        self._id = MachGroupID(next(self._ids))
        self.group_name = MachGroupName(group_name)
        self._machines: dict[MachID, MachineSubtype] = {}
        self._machines_by_name: dict[MachName, MachineSubtype] = {}
        self._machine_type: MachineSubtype | None = None

        if machines is not None:
            checked_machines = self._check_machine_type(machines)

            for mach in checked_machines:
                if mach._id in self._machines:
                    raise MachineError("Duplicate machine in grouping.")
                self._machines[mach._id] = mach
                self._machines_by_name[mach.name] = mach

    def _check_machine_type(
        self, machines: MachineSubtype | list[MachineSubtype]
    ) -> list[MachineSubtype]:

        # First check that it's a valid submachine type and ensure it's in a
        # list
        if not isinstance(machines, list):
            machines = [machines]

        # Now ensure that it's a valid subtype of _Machine and not _Machine
        # itself
        if not all(isinstance(mach, MachineSubtype) for mach in machines):
            raise TypeError("Invalid Machine subtype added to group.")

        # Grab the subtype of the first _Product instance we see and compare
        # everything else against it from then on
        if self._machine_type is None:
            self._machine_type = type(machines[0])  # type: ignore[assignment]

        if not all(type(mach) is self._machine_type for mach in machines):
            raise TypeError(
                "Groups must contain the same Machine types. That is, all"
                " machines must be ContinuousMachine instances or all must"
                " be BatchMachine instances but you cannot have a mixture."
            )

        return machines

    def add_machines(
        self, machines: MachineSubtype | list[MachineSubtype]
    ) -> None:
        """Add a machine or list of machines to an existing grouping.

        Parameters
        ----------
        machines : MachineSubtype | list[MachineSubtype]
            The machine(s) to be added.

        Raises
        ------
        TypeError
            Attempted to add something that wasn't either a ContinuousMachine
            or a BatchMachine to the group.
        TypeError
            Attempted to make a grouping of mixed machine types.
        MachineError
            Attempted to add the same machine twice or more to a grouping.
        """

        checked_machines = self._check_machine_type(machines)

        if any(mach._id in self._machines for mach in checked_machines):
            raise MachineError("Duplicate machine added to grouping.")

        for mach in checked_machines:
            self._machines[mach._id] = mach
            self._machines_by_name[mach.name] = mach

    def add_hard_constraint(
        self, constraints: HardConstraint | list[HardConstraint]
    ) -> None:

        if not isinstance(constraints, list):
            constraints = [constraints]

        if not all(isinstance(item, HardConstraint) for item in constraints):
            raise TypeError("Constraints must all be of type HardConstraint")

        for mach in self._machines.values():
            for item in mach._products.values():
                prod = item["product"]
                for constraint in constraints:
                    cons = deepcopy(constraint)
                    cons._set_product(prod)

                    prod.add_hard_constraint(
                        cons, _level=ConstraintLevel.MACHINE_GROUP.value
                    )


class BatchMachine(_Machine):
    def __init__(self, name: str) -> None:
        super().__init__(name=name)


MachineSubtype = BatchMachine | ContinuousMachine
