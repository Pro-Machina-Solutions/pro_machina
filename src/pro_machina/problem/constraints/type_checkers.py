from ...exceptions import ConstraintError
from ..machines import ContinuousMachine, _Machine
from ..products import ContinuousProduct, _Product
from . import Constraint


def check_continuous_prod_only(constraint: Constraint, product: _Product):
    if not isinstance(product, ContinuousProduct):
        raise ConstraintError(
            f"{type(constraint).__name__} cannot be added to"
            f" product: {product.name}"
        )


def check_continuous_machine_only(constraint: Constraint, machine: _Machine):
    if not isinstance(machine, ContinuousMachine):
        raise ConstraintError(
            f"{type(constraint).__name__} cannot be added to"
            f" machine: {machine.name}"
        )
