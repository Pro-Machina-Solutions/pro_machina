import pytest

from pro_machina.durations import Weeks
from pro_machina.measures import BaseUnit, CustomUnit, Kilo, Unit, Weight
from pro_machina.problem import (
    Consumable,
    ContinuousProduct,
    DemandForecast,
    MadeToStock,
    Problem,
)


def test_mts_no_end_date_requires_freq():
    problem = Problem(start_date="2026-09-28", length=Weeks(3))
    prod_1 = ContinuousProduct("Prod 1", base_dimension=BaseUnit)
    with pytest.raises(ValueError, match="Either a frequency or an end date"):
        mts = MadeToStock(prod_1, qty=Unit(4500), start_date="2026-09-28")

    # Should be fine
    mts = MadeToStock(
        prod_1, qty=Unit(4500), start_date="2026-09-28", freq=Weeks(1)
    )

    # Should be fine
    mts = MadeToStock(
        prod_1, qty=Unit(4500), start_date="2026-09-28", end_date="2026-12-31"
    )


def test_mts_no_freq_setting_contained():
    problem = Problem(start_date="2026-09-28", length=Weeks(3))
    cons_1 = Consumable("Cons 1", base_dimension=Weight)
    cons_2 = Consumable("Cons 2", base_dimension=BaseUnit)

    Bag = CustomUnit("Bag", base_dimension=Weight)
    Bag.size_for(cons_1, Kilo(1.2))

    prod_1 = ContinuousProduct("Prod 1", base_dimension=BaseUnit)
    prod_1.add_component(cons_1, qty=Bag(3), per=Unit(10_000))
    prod_1.add_component(cons_2, qty=Unit(4), per=Unit(2))
    mts = MadeToStock(
        prod_1, qty=Unit(4500), start_date="2026-09-28", end_date="2026-10-02"
    )

    forecast = DemandForecast()
    forecast.add_mts(mts)
    forecast._build(problem=problem)
