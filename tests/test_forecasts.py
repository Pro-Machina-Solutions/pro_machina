import numpy as np
import pytest

from pro_machina.durations import Weeks
from pro_machina.measures import (
    BaseUnit,
    CustomUnit,
    FluidVolume,
    Kilo,
    Litre,
    Unit,
    Weight,
)
from pro_machina.problem import (
    Consumable,
    ContinuousProduct,
    DemandForecast,
    MadeToStock,
    Order,
    Orderline,
    Problem,
)

# ===========================================================================
# MadeToStock - Demand numbers
# ===========================================================================


def test_mts_no_end_date_requires_freq():
    prod_1 = ContinuousProduct("Prod 1", base_dimension=BaseUnit)
    with pytest.raises(ValueError, match="Either a frequency or an end date"):
        MadeToStock(prod_1, qty=Unit(4500), start_date="2026-09-28")

    # Should be fine
    MadeToStock(prod_1, qty=Unit(4500), start_date="2026-09-28", freq=Weeks(1))

    # Should be fine
    MadeToStock(
        prod_1, qty=Unit(4500), start_date="2026-09-28", end_date="2026-12-31"
    )


def test_mts_no_freq_totally_contained():

    problem = Problem(start_date="2026-09-28", length=Weeks(3))
    cons_1 = Consumable("Cons 1", base_dimension=Weight)
    cons_2 = Consumable("Cons 2", base_dimension=BaseUnit)

    Bag = CustomUnit("Bag", base_dimension=Weight)
    Bag.size_for(cons_1, Kilo(1.2))

    prod_1 = ContinuousProduct("Prod 1", base_dimension=BaseUnit)
    subprod = ContinuousProduct("Subprod", base_dimension=FluidVolume)
    prod_1.add_component(cons_1, qty=Bag(3), per=Unit(10_000))
    prod_1.add_component(cons_2, qty=Unit(4), per=Unit(2))
    prod_1.add_component(subprod, qty=Litre("0.75"), per=Unit(850))

    mts = MadeToStock(
        prod_1, qty=Unit(4500), start_date="2026-09-28", end_date="2026-10-02"
    )

    forecast = DemandForecast()
    forecast.add_mts(mts)
    forecast._build(problem=problem)

    assert np.isclose(
        forecast._prod_demand_buckets[prod_1._id].sum(),
        4500.0,
    )
    assert np.isclose(
        forecast._prod_demand_buckets[subprod._id].sum(), 3970.58
    )
    assert np.isclose(
        forecast._cons_demand_buckets[cons_1._id].sum(),
        1620.0,
    )
    assert np.isclose(
        forecast._cons_demand_buckets[cons_2._id].sum(),
        9000.0,
    )


def test_mts_no_freq_cut_early():

    problem = Problem(start_date="2026-09-28", length=Weeks(3))
    cons_1 = Consumable("Cons 1", base_dimension=Weight)
    cons_2 = Consumable("Cons 2", base_dimension=BaseUnit)

    Bag = CustomUnit("Bag", base_dimension=Weight)
    Bag.size_for(cons_1, Kilo(1.2))

    prod_1 = ContinuousProduct("Prod 1", base_dimension=BaseUnit)
    subprod = ContinuousProduct("Subprod", base_dimension=FluidVolume)
    prod_1.add_component(cons_1, qty=Bag(3), per=Unit(10_000))
    prod_1.add_component(cons_2, qty=Unit(4), per=Unit(2))
    prod_1.add_component(subprod, qty=Litre("0.75"), per=Unit(850))

    mts = MadeToStock(
        prod_1, qty=Unit(4500), start_date="2026-09-26", end_date="2026-09-30"
    )

    forecast = DemandForecast()
    forecast.add_mts(mts)
    forecast._build(problem=problem)

    assert np.isclose(
        forecast._prod_demand_buckets[prod_1._id].sum(),
        2250.0,
    )
    assert np.isclose(
        forecast._prod_demand_buckets[subprod._id].sum(), 1985.29
    )
    assert np.isclose(
        forecast._cons_demand_buckets[cons_1._id].sum(),
        810.0,
    )
    assert np.isclose(
        forecast._cons_demand_buckets[cons_2._id].sum(),
        4500.0,
    )


def test_mts_no_freq_cut_late():

    problem = Problem(start_date="2026-09-28", length=Weeks(1))
    cons_1 = Consumable("Cons 1", base_dimension=Weight)
    cons_2 = Consumable("Cons 2", base_dimension=BaseUnit)

    Bag = CustomUnit("Bag", base_dimension=Weight)
    Bag.size_for(cons_1, Kilo(1.2))

    prod_1 = ContinuousProduct("Prod 1", base_dimension=BaseUnit)
    subprod = ContinuousProduct("Subprod", base_dimension=FluidVolume)
    prod_1.add_component(cons_1, qty=Bag(3), per=Unit(10_000))
    prod_1.add_component(cons_2, qty=Unit(4), per=Unit(2))
    prod_1.add_component(subprod, qty=Litre("0.75"), per=Unit(850))

    mts = MadeToStock(
        prod_1, qty=Unit(4500), start_date="2026-09-30", end_date="2026-10-06"
    )

    forecast = DemandForecast()
    forecast.add_mts(mts)
    forecast._build(problem=problem)

    assert np.isclose(
        forecast._prod_demand_buckets[prod_1._id].sum(),
        3750.0,
    )
    assert np.isclose(
        forecast._prod_demand_buckets[subprod._id].sum(), 3308.817
    )
    assert np.isclose(
        forecast._cons_demand_buckets[cons_1._id].sum(),
        1350.0,
    )
    assert np.isclose(
        forecast._cons_demand_buckets[cons_2._id].sum(),
        7500.0,
    )


def test_mts_no_freq_cut_early_and_late():

    problem = Problem(start_date="2026-09-28", length=Weeks(1))
    cons_1 = Consumable("Cons 1", base_dimension=Weight)
    cons_2 = Consumable("Cons 2", base_dimension=BaseUnit)

    Bag = CustomUnit("Bag", base_dimension=Weight)
    Bag.size_for(cons_1, Kilo(1.2))

    prod_1 = ContinuousProduct("Prod 1", base_dimension=BaseUnit)
    subprod = ContinuousProduct("Subprod", base_dimension=FluidVolume)
    prod_1.add_component(cons_1, qty=Bag(3), per=Unit(10_000))
    prod_1.add_component(cons_2, qty=Unit(4), per=Unit(2))
    prod_1.add_component(subprod, qty=Litre("0.75"), per=Unit(850))

    mts = MadeToStock(
        prod_1, qty=Unit(4500), start_date="2026-09-26", end_date="2026-10-06"
    )

    forecast = DemandForecast()
    forecast.add_mts(mts)
    forecast._build(problem=problem)

    assert np.isclose(
        forecast._prod_demand_buckets[prod_1._id].sum(),
        3150.0,
    )
    assert np.isclose(
        forecast._prod_demand_buckets[subprod._id].sum(), 2779.41
    )
    assert np.isclose(
        forecast._cons_demand_buckets[cons_1._id].sum(),
        1134.0,
    )
    assert np.isclose(
        forecast._cons_demand_buckets[cons_2._id].sum(),
        6300.0,
    )


# ===========================================================================
# Orders - Demand numbers
# ===========================================================================


def test_order_fully_contained():

    problem = Problem(start_date="2026-09-28", length=Weeks(3))
    cons_1 = Consumable("Cons 1", base_dimension=Weight)
    cons_2 = Consumable("Cons 2", base_dimension=BaseUnit)

    Bag = CustomUnit("Bag", base_dimension=Weight)
    Bag.size_for(cons_1, Kilo(1.2))

    prod_1 = ContinuousProduct("Prod 1", base_dimension=BaseUnit)
    subprod = ContinuousProduct("Subprod", base_dimension=FluidVolume)
    prod_1.add_component(cons_1, qty=Bag(3), per=Unit(10_000))
    prod_1.add_component(cons_2, qty=Unit(4), per=Unit(2))
    prod_1.add_component(subprod, qty=Litre("0.75"), per=Unit(850))

    order = Order(due_date="2026-10-06", name="Test Order")
    order.add_orderlines(Orderline(prod_1, qty=Unit(4500)))

    forecast = DemandForecast()
    forecast.add_order(order)
    forecast._build(problem)

    assert np.isclose(
        forecast._prod_demand_buckets[prod_1._id].sum(),
        4500.0,
    )
    assert np.isclose(
        forecast._prod_demand_buckets[subprod._id].sum(), 3970.58
    )
    assert np.isclose(
        forecast._cons_demand_buckets[cons_1._id].sum(),
        1620.0,
    )
    assert np.isclose(
        forecast._cons_demand_buckets[cons_2._id].sum(),
        9000.0,
    )


def test_order_cut_early():

    problem = Problem(start_date="2026-09-28", length=Weeks(1))
    cons_1 = Consumable("Cons 1", base_dimension=Weight)
    cons_2 = Consumable("Cons 2", base_dimension=BaseUnit)

    Bag = CustomUnit("Bag", base_dimension=Weight)
    Bag.size_for(cons_1, Kilo(1.2))

    prod_1 = ContinuousProduct("Prod 1", base_dimension=BaseUnit)
    subprod = ContinuousProduct("Subprod", base_dimension=FluidVolume)
    prod_1.add_component(cons_1, qty=Bag(3), per=Unit(10_000))
    prod_1.add_component(cons_2, qty=Unit(4), per=Unit(2))
    prod_1.add_component(subprod, qty=Litre("0.75"), per=Unit(850))

    order = Order(due_date="2026-09-30", name="Test Order")
    order.add_orderlines(Orderline(prod_1, qty=Unit(4500)))

    forecast = DemandForecast()
    forecast.add_order(order)
    forecast._build(problem)

    assert np.isclose(
        forecast._prod_demand_buckets[prod_1._id].sum(),
        1285.714,
    )
    assert np.isclose(
        forecast._prod_demand_buckets[subprod._id].sum(), 1134.454
    )
    assert np.isclose(
        forecast._cons_demand_buckets[cons_1._id].sum(),
        462.857,
    )
    assert np.isclose(
        forecast._cons_demand_buckets[cons_2._id].sum(),
        2571.429,
    )


def test_order_cut_late():

    problem = Problem(start_date="2026-09-28", length=Weeks(1))
    cons_1 = Consumable("Cons 1", base_dimension=Weight)
    cons_2 = Consumable("Cons 2", base_dimension=BaseUnit)

    Bag = CustomUnit("Bag", base_dimension=Weight)
    Bag.size_for(cons_1, Kilo(1.2))

    prod_1 = ContinuousProduct("Prod 1", base_dimension=BaseUnit)
    subprod = ContinuousProduct("Subprod", base_dimension=FluidVolume)
    prod_1.add_component(cons_1, qty=Bag(3), per=Unit(10_000))
    prod_1.add_component(cons_2, qty=Unit(4), per=Unit(2))
    prod_1.add_component(subprod, qty=Litre("0.75"), per=Unit(850))

    order = Order(due_date="2026-10-06", name="Test Order")
    order.add_orderlines(Orderline(prod_1, qty=Unit(4500)))

    forecast = DemandForecast()
    forecast.add_order(order)
    forecast._build(problem)

    assert np.isclose(
        forecast._prod_demand_buckets[prod_1._id].sum(), 3857.143
    )
    assert np.isclose(
        forecast._prod_demand_buckets[subprod._id].sum(), 3403.361
    )
    assert np.isclose(
        forecast._cons_demand_buckets[cons_1._id].sum(),
        1388.571,
    )
    assert np.isclose(
        forecast._cons_demand_buckets[cons_2._id].sum(), 7714.286
    )


def test_order_cut_early_and_late():

    problem = Problem(start_date="2026-09-28", length=Weeks(1))
    cons_1 = Consumable("Cons 1", base_dimension=Weight)
    cons_2 = Consumable("Cons 2", base_dimension=BaseUnit)

    Bag = CustomUnit("Bag", base_dimension=Weight)
    Bag.size_for(cons_1, Kilo(1.2))

    prod_1 = ContinuousProduct("Prod 1", base_dimension=BaseUnit)
    subprod = ContinuousProduct("Subprod", base_dimension=FluidVolume)
    prod_1.add_component(cons_1, qty=Bag(3), per=Unit(10_000))
    prod_1.add_component(cons_2, qty=Unit(4), per=Unit(2))
    prod_1.add_component(subprod, qty=Litre("0.75"), per=Unit(850))

    order = Order(
        due_date="2026-10-08", name="Test Order", production_lead_time=Weeks(2)
    )
    order.add_orderlines(Orderline(prod_1, qty=Unit(4500)))

    forecast = DemandForecast()
    forecast.add_order(order)
    forecast._build(problem)

    assert np.isclose(
        forecast._prod_demand_buckets[prod_1._id].sum(),
        2250.0,
    )
    assert np.isclose(
        forecast._prod_demand_buckets[subprod._id].sum(), 1985.294
    )
    assert np.isclose(forecast._cons_demand_buckets[cons_1._id].sum(), 810.0)
    assert np.isclose(forecast._cons_demand_buckets[cons_2._id].sum(), 4500.0)
