# import datetime as dt
import pytest

from pro_machina.durations import Mins

# from pro_machina import ShiftBuilder, ShiftBreak, ShiftPattern
# from pro_machina.util import as_midnight, parse_datetime
from pro_machina.exceptions import MachineError, ShiftDefinitionError
from pro_machina.measures import (
    #     CustomUnit,
    #     Weight,
    #     Kilo,
    #     Volume,
    #     Cu_Centimetre,
    Unit,
)


def test_cont_prod_to_cont_machine(cont_prod, batch_prod, cont_machine):
    assert len(cont_machine._products) == 0
    cont_machine.add_product(cont_prod, Unit(10), Mins(1))
    assert len(cont_machine._products) == 1

    with pytest.raises(MachineError, match="only add ContinuousProduct"):
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
