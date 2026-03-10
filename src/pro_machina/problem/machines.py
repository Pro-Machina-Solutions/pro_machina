from collections.abc import Sequence
from itertools import count
from typing import NotRequired, TypedDict
from warnings import warn

from pro_machina import Config
from pro_machina.durations import Duration
from pro_machina.exceptions import MachineError
from pro_machina.measures import SizedDimension

from .constraints import Constraint, HardConstraint, SoftConstraint
from .products import BatchProduct, ContinuousProduct, _Product
from .shifts import ShiftPattern


class _MachineProduct(TypedDict):
    product: _Product
    hard_constraints: list[HardConstraint]
    soft_constraints: list[SoftConstraint]
    run_rate: NotRequired[SizedDimension]
    run_rate_per: NotRequired[Duration]


class _Machine:
    _ids = count(0)

    def __init__(self, name: str):
        self._id = next(self._ids)
        self.name = name

        self._products: dict[int, _MachineProduct] = {}
        self._shifts: dict[int, ShiftPattern] | ShiftPattern | None = None

    def add_shift(self, shift: dict[int, ShiftPattern] | ShiftPattern):
        self._shifts = shift


class ContinuousMachine(_Machine):
    def __init__(self, name) -> None:
        super().__init__(name)

    def add_product(
        self,
        product: ContinuousProduct,
        run_rate: SizedDimension,
        per: Duration,
    ):

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
            conf = Config()
            if not conf.silence_warnings:
                print()
                warn(
                    (
                        f"{constraint.__class__.__name__} has already"
                        f" been defined for {product.name} and is being"
                        f" overwritten by {constraint} for Machine:"
                        f" {self.name}"
                    ).lstrip(),
                    stacklevel=2,
                )
                print()
            existing_cons = [con for con in existing_cons if con != constraint]
            existing_cons.append(constraint)  # type: ignore
        else:
            existing_cons.append(constraint)  # type: ignore

        if isinstance(constraint, HardConstraint):
            _product["hard_constraints"] = existing_cons  # type: ignore
        else:
            _product["soft_constraints"] = existing_cons  # type: ignore


class BatchMachine(_Machine):
    def __init__(self, name):
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
