import datetime as dt
import json
import uuid
from collections import defaultdict
from copy import deepcopy
from warnings import warn

import numpy as np
import numpy.typing as npt

import pro_machina

from ..config import Config
from ..durations import Duration
from ..exceptions import ConstraintError, ProblemError
from ..util import (
    as_day_start,
    get_problem_buckets,
    parse_datetime,
    to_str_date,
)
from .constraints import (
    Constraint,
    ConstraintArbiter,
    ConstraintLevel,
    HardConstraint,
    SoftConstraint,
)
from .consumables import ConsID
from .forecasts import DemandForecast
from .machines import (
    BatchMachine,
    ContinuousMachine,
    MachID,
    _Machine,
)
from .products import ProdID
from .stocks import InboundStock, StockHolding


def _check_constraint_is_fully_specified(constraint: Constraint) -> None:

    if (hasattr(constraint, "product") and constraint.product is None) or (
        hasattr(constraint, "machine") and constraint.machine is None
    ):
        raise ConstraintError(
            (
                "Constraints on the Problem level must be fully specified"
                " and that's not the case for"
                f" {type(constraint).__name__}. If the constraint takes a "
                " product and a machine, then both must be specified."
            ).lstrip()
        )


class Problem:
    """The main object to store all components involved in the optimisation

    Parameters
    ----------
    start_time : str | dt.datetime | dt.date
        The starting day of the problem. All problems will start at midnight on
        the date that is provided.
    length : Duration
        The duration for the solution time window. For example, Weeks(2) will
        produce a solution for the two weeks (14 days) following the start
        date.
    config : Config | None
        A custom config object setting the solver parameters. If this is not
        provided then the algorithm will run with the default settings. These
        may not be suitable for all problems but they should provide a
        reasonable starting basis for most problems.
    """

    def __init__(
        self,
        start_time: str | dt.datetime | dt.date,
        length: Duration,
        config: Config | None = None,
    ):
        self.config = config if config is not None else Config()

        # Params
        self._user_start_time: dt.datetime | dt.date
        self._user_start_time = parse_datetime(start_time)
        self._start = as_day_start(self._user_start_time)
        self._end = self._start + dt.timedelta(seconds=length.to_seconds())
        self._duration_secs = (self._end - self._start).total_seconds()

        # Flags
        self._is_built = False

        # Constraint arbiter
        self._arbiter = ConstraintArbiter(self._start, self._end, self.config)

        # Solver containers - other things we'll pass to the solver
        self._forecast: DemandForecast | None = None
        self._machines: dict[MachID, _Machine] = {}
        # self._machine_groups: dict[int, dict[int, _Machine]] = {}
        self._starting_stocks: dict[ConsID | ProdID, StockHolding] = {}
        self._inbound_stock: dict[int, InboundStock] = {}

        self._hard_constraints: list[HardConstraint] = []
        self._soft_constraints: list[SoftConstraint] = []

        self._prod_machine_mapping: dict[ProdID, list[MachID]] = defaultdict(
            list
        )
        self._machine_prod_mapping: dict[MachID, list[ProdID]] = {}

        self._machine_base_productivity: dict[
            MachID, npt.NDArray[np.float64]
        ] = {}

        # Problem containers - things we need to make result human-readable
        self._machine_names: dict[MachID, str] = {}
        self._product_names: dict[ProdID, str] = {}
        self._consumable_names: dict[ConsID, str] = {}

    def add_machine(self, machine: BatchMachine | ContinuousMachine) -> None:
        """Add a machine to the problem

        The machine is assumed to be fully specified at this point, including
        all machine-level constraints and all product production specifications
        having been set.

        Parameters
        ----------
        machine : BatchMachine | ContinuousMachine
            The defined machine to be added

        Raises
        ------
        TypeError
            Attempted to add something that isn't of type ContinuousMachine or
            BatchMachine
        ProblemError
            Attempted to add the same machine to a problem twice
        ProblemError
            Attempted to alter a finalised, built problem
        """
        if self._is_built:
            raise ProblemError("Cannot alter a built problem")

        if machine._id in self._machines:
            raise ProblemError("Cannot add the same machine twice")

        if not machine._shifts and not pro_machina.options["silence_warnings"]:
            warn(
                "\n"
                + f"No shift pattern added for {machine.name}. It's assumed to"
                " always be running",
                stacklevel=1,
            )

        # Copy over the machine constraints at this point. Once a machine is
        # added to the problem, no more changes can be made to that machine.
        # Any product constraints, whether or not they are directly tied to
        # that machine, will be carried over too.
        self._hard_constraints.extend(deepcopy(machine._hard_constraints))
        self._soft_constraints.extend(deepcopy(machine._soft_constraints))

        # Set the mappings
        self._machine_prod_mapping[machine._id] = list(
            machine._products.keys()
        )
        for prod_id in machine._products.keys():
            self._prod_machine_mapping[prod_id].append(machine._id)

        self._machines[machine._id] = machine

    def add_stock(self, stock: StockHolding) -> None:
        """Add units of stock available at the problem start date

        If the starting stock is added more than once (for example, it appears
        in two or more data sources you are drawing from) then a warning will
        be issued (unless silenced) and the last value seen will be used.

        Parameters
        ----------
        stock : StockHolding
            A SizedDimension type stating the starting stock

        Raises
        ------
        TypeError
            Attempted to add something that isn't of type StockHolding
        ProblemError
            Attempted to alter a finalised, built problem
        """
        if self._is_built:
            raise ProblemError("Cannot alter a built problem")

        if not isinstance(stock, StockHolding):
            raise TypeError("Starting stock type not recognised")

        if (
            stock._id in self._starting_stocks
            and not pro_machina.options["silence_warnings"]
        ):
            warn(
                "\n" + f"{stock.item.name} starting stock being overwritten",
                stacklevel=1,
            )
        self._starting_stocks[stock._id] = stock

    def add_inbound_stock(self, inbound: InboundStock) -> None:
        """Add units of consumable stock becoming available during the problem

        Parameters
        ----------
        stock : InboundStock
            A SizedDimension type stating the quantity of consumable arriving
            on site on a specific date

        Raises
        ------
        TypeError
            Attempted to add something that isn't of type InboundStock
        ProblemError
            Attempted to alter a finalised, built problem
        """
        if self._is_built:
            raise ProblemError("Cannot alter a built problem")

        if not isinstance(inbound, InboundStock):
            raise TypeError("Inbound stock type not recognised")

        self._inbound_stock[inbound._id] = inbound

    def set_forecast(self, forecast: DemandForecast):
        """Set the forecast for orders and made to stock quantities

        Parameters
        ----------
        forecast : DemandForecast
            A DemandForecast detailing all product demands for the site

        Raises
        ------
        TypeError
            Attempted to add something that isn't of type DemandForecast
        ProblemError
            Attempted to alter a finalised, built problem
        """
        if self._is_built:
            raise ProblemError("Cannot alter a built problem")

        if not isinstance(forecast, DemandForecast):
            raise TypeError("Invalid forecast type")

        self._forecast = forecast

    def add_hard_constraint(
        self, constraints: HardConstraint | list[HardConstraint]
    ) -> None:
        """Add a hard constraint at the problem level

        In this case, a hard constraint can be added directly to the problem,
        which supercedes any other constraints that have been defined either on
        the product or machine level. For this, the constraint **must** specify
        the machine and the product that it applies to.

        Parameters
        ----------
        constraint : HardConstraint
            The hard constraint being applied to the machine-product pairing

        Raises
        ------
        TypeError
            Raised when passing something other than a HardConstraint
        ConstraintError
            Raised when the constraint does not specify the minimum criteria
            to fully define it
        ProblemError
            Attempted to alter a finalised, built problem
        """

        if self._is_built:
            raise ProblemError("Cannot alter a built problem")

        if isinstance(constraints, HardConstraint):
            constraints = [constraints]

        if not all(isinstance(item, HardConstraint) for item in constraints):
            raise TypeError("Constraints must all be of type HardConstraint")

        for constraint in constraints:
            _check_constraint_is_fully_specified(constraint)
            constraint._level = ConstraintLevel.PROBLEM.value

        self._hard_constraints.extend(constraints)

    def add_soft_constraint(self, constraint: SoftConstraint) -> None:
        """Add a soft constraint at the problem level

        In this case, a soft constraint can be added directly to the problem,
        which supercedes any other constraints that have been defined either on
        the product or machine level. For this, the constraint **must** specify
        the machine and the product that it applies to.

        Parameters
        ----------
        constraint : SoftConstraint
            The soft constraint being applied to the machine-product pairing

        Raises
        ------
        TypeError
            Raised when passing something other than a SoftConstraint
        ConstraintError
            Raised when the constraint does not specify the minimum criteria
            to fully define it
        ProblemError
            Attempted to alter a finalised, built problem
        """

        if self._is_built:
            raise ProblemError("Cannot alter a built problem")

        if not isinstance(constraint, SoftConstraint):
            raise TypeError(
                f"{constraint.__class__.__name__} is not a soft constraint"
            )

        _check_constraint_is_fully_specified(constraint)

        if (
            constraint in self._soft_constraints
            and not pro_machina.options["silence_constraint_overrides"]
        ):
            warn(
                f"\n{constraint.__class__.__name__} has been specified for"
                f" product: {constraint.product} and machine:"
                f" {constraint.machine} already and is being set at the"
                " problem level",
                stacklevel=1,
            )
        # self._soft_constraints.add(constraint)

    def build(self) -> None:
        """Finalise the problem to be passed to the solver

        Once the problem has been built, no further alterations can be made to
        the problem definition. This is because multiple pre-processing steps
        will occur at this point to prepare the data for dispatch to the
        solver. Problems cannot be solved until they have been built.

        Raises
        ------
        ProblemError
            No demand forecast has been set
        ProblemError
            No machines have been added to the problem
        """
        if self._forecast is None:
            raise ProblemError("No demand forecast has been set")

        if not self._machines:
            raise ProblemError("No machines have been defined")

        for machine_id, machine in self._machines.items():
            self._machine_base_productivity[machine_id] = (
                machine._build_shift_productivity(self).tolist()
            )
            self._machine_names[machine_id] = machine.name
            for prod_id, machine_prod in machine._products.items():
                self._product_names[prod_id] = machine_prod["product"].name

        self._forecast._build(self)
        self._product_names = (
            self._product_names | self._forecast._product_names
        )
        self._arbiter.arbitrate_hard_constraints(
            self._hard_constraints,
            self._prod_machine_mapping,
            self._machine_prod_mapping,
        )
        self._is_built = True

    def solve(self) -> None:
        if not self._is_built:
            raise ProblemError("The problem has not been built")

        payload = {
            "start_date": to_str_date(self._start),
            "bucket_duration_secs": self.config.timebucket.to_seconds(),
            "num_buckets": get_problem_buckets(
                self._start, self._end, self.config.timebucket
            ),
            "problem_id": uuid.uuid4().hex,
        }

        payload["machine_productivity"] = self._machine_base_productivity

        assert self._forecast is not None

        prod_demands = self._forecast._prod_demands
        for k, v in prod_demands.items():
            prod_demands[k] = v.tolist()

        cons_demands = self._forecast._cons_demands
        for k, v in cons_demands.items():
            cons_demands[k] = v.tolist()

        payload["product_forecast"] = prod_demands
        payload["consumable_forecast"] = cons_demands

        with open("payload.json", "w") as outfile:
            json.dump(payload, outfile, indent=4)
