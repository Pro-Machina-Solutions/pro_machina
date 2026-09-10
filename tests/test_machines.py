# import datetime as dt
import pytest

from pro_machina import (
    ContinuousMachine,
    ContinuousProduct,
)
from pro_machina.durations import Mins

# from pro_machina import ShiftBuilder, ShiftBreak, ShiftPattern
# from pro_machina.util import as_midnight, parse_datetime
from pro_machina.exceptions import UnitError
from pro_machina.measures import (
    BaseUnit,
    CustomUnit,
    Litre,
    #     CustomUnit,
    #     Weight,
    #     Kilo,
    #     Volume,
    #     Cu_Centimetre,
    Unit,
)

"""
def test_cont_prod_to_cont_machine_only(cont_prod, batch_prod, cont_machine):
    assert len(cont_machine._products) == 0
    cont_machine.add_product(cont_prod, Unit(10), Mins(1))
    assert len(cont_machine._products) == 1

    with pytest.raises(TypeError, match="only add ContinuousProduct"):
        cont_machine.add_product(batch_prod, Unit(10), Mins(1))


def test_blanket_add_simple_shift(cont_machine, simple_shift):
    cont_machine.add_shift(simple_shift)

    with pytest.raises(TypeError):
        cont_machine.add_shift("Hello")


def test_shift_pattern_start_end_correct(cont_machine, simple_shift):
    # Should be fine
    cont_machine.add_shift(simple_shift, start_date="2026-10-01")

    with pytest.raises(ShiftDefinitionError):
        cont_machine.add_shift(simple_shift, end_date="2026-10-01")

    with pytest.raises(ValueError):
        cont_machine.add_shift(
            simple_shift, start_date="2026-10-02", end_date="2026-10-01"
        )


def test_machine_default_on(base_problem: Problem, cont_machine):
    base_problem.set_forecast(DemandForecast())
    base_problem.add_machine(cont_machine)
    base_problem.build()
    assert sum(base_problem._machine_base_productivity[0]) == 67200  # type: ignore
"""

# ===========================================================================
# Production unit restrictions
# ===========================================================================


def test_compatible_base_units_work():
    # No default run rate. Should work when specified
    prod = ContinuousProduct("Prod 1", base_dimension=BaseUnit)
    mach = ContinuousMachine("Mach 1")
    mach.add_product(prod, run_rate=Unit(10), per=Mins(1))

    # Try with default rate. Should also work
    prod = ContinuousProduct("Prod 1", base_dimension=BaseUnit)
    mach = ContinuousMachine(
        "Mach 1", default_run_rate=Unit(10), default_per=Mins(1)
    )
    mach.add_product(prod)


def test_incompatible_base_units_fail():
    # Without defaults
    prod = ContinuousProduct("Prod 1", base_dimension=BaseUnit)
    mach = ContinuousMachine("Mach 1")
    with pytest.raises(UnitError, match="Production units of Litre"):
        mach.add_product(prod, run_rate=Litre(10), per=Mins(1))

    # With defaults
    prod = ContinuousProduct("Prod 1", base_dimension=BaseUnit)
    mach = ContinuousMachine(
        "Mach 1", default_run_rate=Litre(10), default_per=Mins(1)
    )
    with pytest.raises(UnitError, match="Production units of Litre"):
        mach.add_product(prod)


def test_compatible_custom_units_work_1():
    Case = CustomUnit("Case", dimension=BaseUnit)

    # No default run rate. Should work when specified
    prod = ContinuousProduct("Prod 1", base_dimension=BaseUnit)
    Case.size_for(prod, Unit(10))

    mach = ContinuousMachine("Mach 1")
    mach.add_product(prod, run_rate=Case(1), per=Mins(1))


def test_compatible_custom_units_work_2():
    Case = CustomUnit("Case", dimension=BaseUnit)

    # With default rate
    prod = ContinuousProduct("Prod 1", base_dimension=BaseUnit)
    Case.size_for(prod, Unit(10))

    mach = ContinuousMachine(
        "Mach 1", default_run_rate=Case(2), default_per=Mins(1)
    )
    mach.add_product(prod)


def test_incompatible_custom_unit_rate_fails_1():
    Case = CustomUnit("Case", dimension=BaseUnit)

    prod = ContinuousProduct("Prod 1", base_dimension=BaseUnit)
    Case.size_for(prod, Unit(10))

    # Without default run rate
    mach = ContinuousMachine("Mach 1")
    with pytest.raises(UnitError, match="Production units of Litre"):
        mach.add_product(prod, run_rate=Litre(10), per=Mins(1))


def test_incompatible_custom_unit_rate_fails_2():
    Case = CustomUnit("Case", dimension=BaseUnit)

    prod = ContinuousProduct("Prod 1", base_dimension=BaseUnit)
    Case.size_for(prod, Unit(10))

    # With default run rate
    mach = ContinuousMachine(
        "Mach 1", default_run_rate=Litre(10), default_per=Mins(1)
    )
    with pytest.raises(UnitError, match="Production units of Litre"):
        mach.add_product(prod)
