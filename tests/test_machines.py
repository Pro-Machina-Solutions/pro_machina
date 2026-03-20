# import datetime as dt
import pytest

from pro_machina.durations import Mins

# from pro_machina import ShiftBuilder, ShiftBreak, ShiftPattern
# from pro_machina.util import as_midnight, parse_datetime
from pro_machina.exceptions import MachineError
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
