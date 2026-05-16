from ...exceptions import ConstraintError
from ..machines import ContinuousMachine
from ..products import ContinuousProduct
from . import Constraint


def check_continuous_prod_only(
    constraint: Constraint, product: ContinuousProduct
):
    if not isinstance(product, ContinuousProduct):
        raise ConstraintError(
            (
                f"{constraint.__class__.__name__} cannot be added to"
                f" product: {product.name}"
            ).lstrip()
        )


def check_continuous_machine_only(
    constraint: Constraint, machine: ContinuousMachine
):
    if not isinstance(machine, ContinuousMachine):
        raise ConstraintError(
            (
                f"{constraint.__class__.__name__} cannot be added to"
                f" machine: {machine.name}"
            ).lstrip()
        )
