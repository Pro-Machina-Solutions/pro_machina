import datetime as dt

import numpy as np
import pytest

from pro_machina.durations import Days, Hours, Weeks
from pro_machina.exceptions import UnitError
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
    ProductGroup,
)
from pro_machina.problem.hard_constraints import MinProductionTime

# ===========================================================================
# MadeToStock - Demand numbers - No freq
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
    sub = ContinuousProduct("Subprod", base_dimension=FluidVolume)
    prod_1.add_component(cons_1, qty=Bag(3), per=Unit(10_000))
    prod_1.add_component(cons_2, qty=Unit(4), per=Unit(2))
    prod_1.add_component(sub, qty=Litre("0.75"), per=Unit(850))

    mts = MadeToStock(
        prod_1, qty=Unit(4500), start_date="2026-09-28", end_date="2026-10-02"
    )

    forecast = DemandForecast()
    forecast.add_mts(mts)
    forecast._build(problem=problem)

    assert np.isclose(forecast._prod_demand_buckets[prod_1._id].sum(), 4500.0)
    assert np.isclose(forecast._prod_demand_buckets[sub._id].sum(), 3970.58)
    assert np.isclose(forecast._cons_demand_buckets[cons_1._id].sum(), 1620.0)
    assert np.isclose(forecast._cons_demand_buckets[cons_2._id].sum(), 9000.0)


def test_mts_no_freq_cut_early():

    problem = Problem(start_date="2026-09-28", length=Weeks(3))
    cons_1 = Consumable("Cons 1", base_dimension=Weight)
    cons_2 = Consumable("Cons 2", base_dimension=BaseUnit)

    Bag = CustomUnit("Bag", base_dimension=Weight)
    Bag.size_for(cons_1, Kilo(1.2))

    prod_1 = ContinuousProduct("Prod 1", base_dimension=BaseUnit)
    sub = ContinuousProduct("Subprod", base_dimension=FluidVolume)
    prod_1.add_component(cons_1, qty=Bag(3), per=Unit(10_000))
    prod_1.add_component(cons_2, qty=Unit(4), per=Unit(2))
    prod_1.add_component(sub, qty=Litre("0.75"), per=Unit(850))

    mts = MadeToStock(
        prod_1, qty=Unit(4500), start_date="2026-09-26", end_date="2026-09-30"
    )

    forecast = DemandForecast()
    forecast.add_mts(mts)
    forecast._build(problem=problem)

    assert np.isclose(forecast._prod_demand_buckets[prod_1._id].sum(), 2250.0)
    assert np.isclose(forecast._prod_demand_buckets[sub._id].sum(), 1985.29)
    assert np.isclose(forecast._cons_demand_buckets[cons_1._id].sum(), 810.0)
    assert np.isclose(forecast._cons_demand_buckets[cons_2._id].sum(), 4500.0)


def test_mts_no_freq_cut_late():

    problem = Problem(start_date="2026-09-28", length=Weeks(1))
    cons_1 = Consumable("Cons 1", base_dimension=Weight)
    cons_2 = Consumable("Cons 2", base_dimension=BaseUnit)

    Bag = CustomUnit("Bag", base_dimension=Weight)
    Bag.size_for(cons_1, Kilo(1.2))

    prod_1 = ContinuousProduct("Prod 1", base_dimension=BaseUnit)
    sub = ContinuousProduct("Subprod", base_dimension=FluidVolume)
    prod_1.add_component(cons_1, qty=Bag(3), per=Unit(10_000))
    prod_1.add_component(cons_2, qty=Unit(4), per=Unit(2))
    prod_1.add_component(sub, qty=Litre("0.75"), per=Unit(850))

    mts = MadeToStock(
        prod_1, qty=Unit(4500), start_date="2026-09-30", end_date="2026-10-06"
    )

    forecast = DemandForecast()
    forecast.add_mts(mts)
    forecast._build(problem=problem)

    assert np.isclose(forecast._prod_demand_buckets[prod_1._id].sum(), 3750.0)
    assert np.isclose(forecast._prod_demand_buckets[sub._id].sum(), 3308.817)
    assert np.isclose(forecast._cons_demand_buckets[cons_1._id].sum(), 1350.0)
    assert np.isclose(forecast._cons_demand_buckets[cons_2._id].sum(), 7500.0)


def test_mts_no_freq_cut_early_and_late():

    problem = Problem(start_date="2026-09-28", length=Weeks(1))
    cons_1 = Consumable("Cons 1", base_dimension=Weight)
    cons_2 = Consumable("Cons 2", base_dimension=BaseUnit)

    Bag = CustomUnit("Bag", base_dimension=Weight)
    Bag.size_for(cons_1, Kilo(1.2))

    prod_1 = ContinuousProduct("Prod 1", base_dimension=BaseUnit)
    sub = ContinuousProduct("Subprod", base_dimension=FluidVolume)
    prod_1.add_component(cons_1, qty=Bag(3), per=Unit(10_000))
    prod_1.add_component(cons_2, qty=Unit(4), per=Unit(2))
    prod_1.add_component(sub, qty=Litre("0.75"), per=Unit(850))

    mts = MadeToStock(
        prod_1, qty=Unit(4500), start_date="2026-09-26", end_date="2026-10-06"
    )

    forecast = DemandForecast()
    forecast.add_mts(mts)
    forecast._build(problem=problem)

    assert np.isclose(forecast._prod_demand_buckets[prod_1._id].sum(), 3150.0)
    assert np.isclose(forecast._prod_demand_buckets[sub._id].sum(), 2779.41)
    assert np.isclose(forecast._cons_demand_buckets[cons_1._id].sum(), 1134.0)
    assert np.isclose(forecast._cons_demand_buckets[cons_2._id].sum(), 6300.0)


# ===========================================================================
# MadeToStock - Demand numbers - With freq
# ===========================================================================


def test_repeat_inside_problem_window():
    problem = Problem(start_date="2026-09-28", length=Weeks(3))
    cons_1 = Consumable("Cons 1", base_dimension=Weight)
    cons_2 = Consumable("Cons 2", base_dimension=BaseUnit)

    Bag = CustomUnit("Bag", base_dimension=Weight)
    Bag.size_for(cons_1, Kilo(1.2))

    prod_1 = ContinuousProduct("Prod 1", base_dimension=BaseUnit)
    sub = ContinuousProduct("Subprod", base_dimension=FluidVolume)
    prod_1.add_component(cons_1, qty=Bag(3), per=Unit(10_000))
    prod_1.add_component(cons_2, qty=Unit(4), per=Unit(2))
    prod_1.add_component(sub, qty=Litre("0.75"), per=Unit(850))

    mts = MadeToStock(
        prod_1, qty=Unit(4500), start_date="2026-09-28", freq=Weeks(1)
    )

    forecast = DemandForecast()
    forecast.add_mts(mts)
    forecast._build(problem=problem)

    assert np.isclose(forecast._prod_demand_buckets[prod_1._id].sum(), 13500.0)
    assert np.isclose(forecast._prod_demand_buckets[sub._id].sum(), 11911.765)
    assert np.isclose(forecast._cons_demand_buckets[cons_1._id].sum(), 4860.0)
    assert np.isclose(forecast._cons_demand_buckets[cons_2._id].sum(), 27000.0)


def test_repeat_overspills_problem_window():
    problem = Problem(start_date="2026-09-28", length=Weeks(3))
    cons_1 = Consumable("Cons 1", base_dimension=Weight)
    cons_2 = Consumable("Cons 2", base_dimension=BaseUnit)

    Bag = CustomUnit("Bag", base_dimension=Weight)
    Bag.size_for(cons_1, Kilo(1.2))

    prod_1 = ContinuousProduct("Prod 1", base_dimension=BaseUnit)
    sub = ContinuousProduct("Subprod", base_dimension=FluidVolume)
    prod_1.add_component(cons_1, qty=Bag(3), per=Unit(10_000))
    prod_1.add_component(cons_2, qty=Unit(4), per=Unit(2))
    prod_1.add_component(sub, qty=Litre("0.75"), per=Unit(850))

    mts = MadeToStock(
        prod_1, qty=Unit(4500), start_date="2026-09-28", freq=Days(6)
    )

    forecast = DemandForecast()
    forecast.add_mts(mts)
    forecast._build(problem=problem)

    assert np.isclose(forecast._prod_demand_buckets[prod_1._id].sum(), 15750.0)
    assert np.isclose(forecast._prod_demand_buckets[sub._id].sum(), 13897.06)
    assert np.isclose(forecast._cons_demand_buckets[cons_1._id].sum(), 5670.0)
    assert np.isclose(forecast._cons_demand_buckets[cons_2._id].sum(), 31500.0)


def test_repeat_underspills_problem_window():
    problem = Problem(start_date="2026-09-28", length=Weeks(3))
    cons_1 = Consumable("Cons 1", base_dimension=Weight)
    cons_2 = Consumable("Cons 2", base_dimension=BaseUnit)

    Bag = CustomUnit("Bag", base_dimension=Weight)
    Bag.size_for(cons_1, Kilo(1.2))

    prod_1 = ContinuousProduct("Prod 1", base_dimension=BaseUnit)
    sub = ContinuousProduct("Subprod", base_dimension=FluidVolume)
    prod_1.add_component(cons_1, qty=Bag(3), per=Unit(10_000))
    prod_1.add_component(cons_2, qty=Unit(4), per=Unit(2))
    prod_1.add_component(sub, qty=Litre("0.75"), per=Unit(850))

    mts = MadeToStock(
        prod_1, qty=Unit(4500), start_date="2026-09-26", freq=Days(6)
    )

    forecast = DemandForecast()
    forecast.add_mts(mts)
    forecast._build(problem=problem)

    assert np.isclose(forecast._prod_demand_buckets[prod_1._id].sum(), 15750.0)
    assert np.isclose(forecast._prod_demand_buckets[sub._id].sum(), 13897.06)
    assert np.isclose(forecast._cons_demand_buckets[cons_1._id].sum(), 5670.0)
    assert np.isclose(forecast._cons_demand_buckets[cons_2._id].sum(), 31500.0)


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
    sub = ContinuousProduct("Subprod", base_dimension=FluidVolume)
    prod_1.add_component(cons_1, qty=Bag(3), per=Unit(10_000))
    prod_1.add_component(cons_2, qty=Unit(4), per=Unit(2))
    prod_1.add_component(sub, qty=Litre("0.75"), per=Unit(850))

    order = Order(due_date="2026-10-06", name="Test Order")
    order.add_orderlines(Orderline(prod_1, qty=Unit(4500)))

    forecast = DemandForecast()
    forecast.add_order(order)
    forecast._build(problem)

    assert np.isclose(forecast._prod_demand_buckets[prod_1._id].sum(), 4500.0)
    assert np.isclose(forecast._prod_demand_buckets[sub._id].sum(), 3970.58)
    assert np.isclose(forecast._cons_demand_buckets[cons_1._id].sum(), 1620.0)
    assert np.isclose(forecast._cons_demand_buckets[cons_2._id].sum(), 9000.0)


def test_order_cut_early():

    problem = Problem(start_date="2026-09-28", length=Weeks(1))
    cons_1 = Consumable("Cons 1", base_dimension=Weight)
    cons_2 = Consumable("Cons 2", base_dimension=BaseUnit)

    Bag = CustomUnit("Bag", base_dimension=Weight)
    Bag.size_for(cons_1, Kilo(1.2))

    prod_1 = ContinuousProduct("Prod 1", base_dimension=BaseUnit)
    sub = ContinuousProduct("Subprod", base_dimension=FluidVolume)
    prod_1.add_component(cons_1, qty=Bag(3), per=Unit(10_000))
    prod_1.add_component(cons_2, qty=Unit(4), per=Unit(2))
    prod_1.add_component(sub, qty=Litre("0.75"), per=Unit(850))

    order = Order(due_date="2026-09-30", name="Test Order")
    order.add_orderlines(Orderline(prod_1, qty=Unit(4500)))

    forecast = DemandForecast()
    forecast.add_order(order)
    forecast._build(problem)

    assert np.isclose(forecast._prod_demand_buckets[prod_1._id].sum(), 1285.71)
    assert np.isclose(forecast._prod_demand_buckets[sub._id].sum(), 1134.454)
    assert np.isclose(forecast._cons_demand_buckets[cons_1._id].sum(), 462.857)
    assert np.isclose(forecast._cons_demand_buckets[cons_2._id].sum(), 2571.43)


def test_order_cut_late():

    problem = Problem(start_date="2026-09-28", length=Weeks(1))
    cons_1 = Consumable("Cons 1", base_dimension=Weight)
    cons_2 = Consumable("Cons 2", base_dimension=BaseUnit)

    Bag = CustomUnit("Bag", base_dimension=Weight)
    Bag.size_for(cons_1, Kilo(1.2))

    prod_1 = ContinuousProduct("Prod 1", base_dimension=BaseUnit)
    sub = ContinuousProduct("Subprod", base_dimension=FluidVolume)
    prod_1.add_component(cons_1, qty=Bag(3), per=Unit(10_000))
    prod_1.add_component(cons_2, qty=Unit(4), per=Unit(2))
    prod_1.add_component(sub, qty=Litre("0.75"), per=Unit(850))

    order = Order(due_date="2026-10-06", name="Test Order")
    order.add_orderlines(Orderline(prod_1, qty=Unit(4500)))

    forecast = DemandForecast()
    forecast.add_order(order)
    forecast._build(problem)

    assert np.isclose(forecast._prod_demand_buckets[prod_1._id].sum(), 3857.14)
    assert np.isclose(forecast._prod_demand_buckets[sub._id].sum(), 3403.36)
    assert np.isclose(forecast._cons_demand_buckets[cons_1._id].sum(), 1388.57)
    assert np.isclose(forecast._cons_demand_buckets[cons_2._id].sum(), 7714.28)


def test_order_cut_early_and_late():

    problem = Problem(start_date="2026-09-28", length=Weeks(1))
    cons_1 = Consumable("Cons 1", base_dimension=Weight)
    cons_2 = Consumable("Cons 2", base_dimension=BaseUnit)

    Bag = CustomUnit("Bag", base_dimension=Weight)
    Bag.size_for(cons_1, Kilo(1.2))

    prod_1 = ContinuousProduct("Prod 1", base_dimension=BaseUnit)
    sub = ContinuousProduct("Subprod", base_dimension=FluidVolume)
    prod_1.add_component(cons_1, qty=Bag(3), per=Unit(10_000))
    prod_1.add_component(cons_2, qty=Unit(4), per=Unit(2))
    prod_1.add_component(sub, qty=Litre("0.75"), per=Unit(850))

    order = Order(
        due_date="2026-10-08", name="Test Order", production_lead_time=Weeks(2)
    )
    order.add_orderlines(Orderline(prod_1, qty=Unit(4500)))

    forecast = DemandForecast()
    forecast.add_order(order)
    forecast._build(problem)

    assert np.isclose(forecast._prod_demand_buckets[prod_1._id].sum(), 2250.0)
    assert np.isclose(forecast._prod_demand_buckets[sub._id].sum(), 1985.294)
    assert np.isclose(forecast._cons_demand_buckets[cons_1._id].sum(), 810.0)
    assert np.isclose(forecast._cons_demand_buckets[cons_2._id].sum(), 4500.0)


# ===========================================================================
# Shared helpers for control-flow tests
# ===========================================================================
#
# These tests check behaviour (validation, branching, accumulation) rather
# than interpolation maths, so they use 1:1 bills of materials and round
# quantities to keep the expected values obvious.
#
# Production windows are half-open, [start, end): production can happen at
# the start but not at the end. So an order gets no production on its due
# date, and a window running past the problem end keeps the problem's last
# day (the problem itself being [start, end)).


def _simple_product(name="Ctrl Prod", sub_name=None, cons_name=None):
    """Product in Units with optional 1:1 subproduct and consumable."""
    prod = ContinuousProduct(name, base_dimension=BaseUnit)
    sub = cons = None
    if sub_name is not None:
        sub = ContinuousProduct(sub_name, base_dimension=BaseUnit)
        prod.add_component(sub, qty=Unit(1), per=Unit(1))
    if cons_name is not None:
        cons = Consumable(cons_name, base_dimension=BaseUnit)
        prod.add_component(cons, qty=Unit(1), per=Unit(1))
    return prod, sub, cons


def _one_week_problem():
    # 2026-09-28 -> 2026-10-05, 15 minute buckets (672 in total)
    return Problem(start_date="2026-09-28", length=Weeks(1))


BUCKETS_PER_DAY = 96


# ===========================================================================
# Order - construction and validation
# ===========================================================================


def test_order_requires_name_or_code():
    with pytest.raises(ValueError, match="Either a name or a code"):
        Order(due_date="2026-10-06")


def test_order_accepts_code_without_name():
    order = Order(due_date="2026-10-06", code="ORD-001")

    assert order.name is None
    assert order.code == "ORD-001"


def test_order_due_date_is_start_of_day():
    order = Order(due_date="2026-10-06 15:45:00", name="Ctrl Order")

    assert order.due_date == dt.datetime(2026, 10, 6)


def test_order_lines_via_constructor_single_and_list():
    prod_a, _, _ = _simple_product("Ctrl A")
    prod_b, _, _ = _simple_product("Ctrl B")

    single = Order(
        due_date="2026-10-06",
        name="Ctrl Single",
        lines=Orderline(prod_a, qty=Unit(10)),
    )
    multi = Order(
        due_date="2026-10-06",
        name="Ctrl Multi",
        lines=[Orderline(prod_a, qty=Unit(10)), Orderline(prod_b, Unit(5))],
    )

    assert [line.product for line in single._lines.values()] == [prod_a]
    assert {line.product for line in multi._lines.values()} == {
        prod_a,
        prod_b,
    }


@pytest.mark.parametrize("bad", ["not a line", 42, ["also not a line"]])
def test_add_orderlines_rejects_non_orderline(bad):
    order = Order(due_date="2026-10-06", name="Ctrl Bad Lines")

    with pytest.raises(TypeError, match="Not a valid Orderline type"):
        order.add_orderlines(bad)


def test_add_orderlines_rejects_mixed_list_without_adding_any():
    prod, _, _ = _simple_product()
    order = Order(due_date="2026-10-06", name="Ctrl Mixed Lines")

    with pytest.raises(TypeError, match="Not a valid Orderline type"):
        order.add_orderlines([Orderline(prod, Unit(1)), "not a line"])

    assert order._lines == {}


def test_add_same_orderline_twice_warns():
    prod, _, _ = _simple_product()
    order = Order(due_date="2026-10-06", name="Ctrl Dup Lines")
    line = Orderline(prod, Unit(5))
    order.add_orderlines(line)

    with pytest.warns(UserWarning, match="added more than once"):
        order.add_orderlines(line)

    assert list(order._lines.values()) == [line]


def test_two_lines_for_same_product_are_both_kept():
    prod, _, _ = _simple_product()
    order = Order(due_date="2026-10-06", name="Ctrl Two Lines")
    order.add_orderlines([Orderline(prod, Unit(5)), Orderline(prod, Unit(7))])

    assert sorted(line.qty._base_qty for line in order._lines.values()) == [
        5,
        7,
    ]


def test_order_accepts_hard_constraint():
    Order(
        due_date="2026-10-06",
        name="Ctrl Constrained",
        hard_constraints=MinProductionTime(Hours(4)),
    )


def test_order_empty_constraint_lists_are_fine():
    # Empty lists skip the isinstance checks entirely
    Order(
        due_date="2026-10-06",
        name="Ctrl Empty Constraints",
        hard_constraints=[],
        soft_constraints=[],
    )


# ===========================================================================
# Orderline - quantity handling
# ===========================================================================


def test_orderline_resolves_custom_unit():
    prod, _, _ = _simple_product()
    Case = CustomUnit("Ctrl Case", base_dimension=BaseUnit)
    Case.size_for(prod, Unit(24))

    line = Orderline(prod, qty=Case(5))

    assert line.qty._base_qty == 120


def test_orderline_bare_number_raises_type_error():
    prod, _, _ = _simple_product()

    with pytest.raises(TypeError, match="Expected a measure"):
        Orderline(prod, qty=100)


def test_orderline_incompatible_measure_raises_unit_error():
    prod, _, _ = _simple_product()

    with pytest.raises(UnitError, match="invalid measure"):
        Orderline(prod, qty=Kilo(5))


def test_orderline_unsized_custom_unit_raises_unit_error():
    prod, _, _ = _simple_product()
    Crate = CustomUnit("Ctrl Crate")

    with pytest.raises(UnitError, match="has not been sized for"):
        Orderline(prod, qty=Crate(1))


# ===========================================================================
# MadeToStock - construction and validation
# ===========================================================================


@pytest.mark.parametrize("bad", ["Prod 1", 42, None])
def test_mts_rejects_non_product(bad):
    with pytest.raises(TypeError, match="Not a valid Product or Product"):
        MadeToStock(bad, qty=Unit(1), start_date="2026-09-28", freq=Weeks(1))


def test_mts_bare_number_raises_type_error():
    prod, _, _ = _simple_product()

    with pytest.raises(TypeError, match="Expected a measure"):
        MadeToStock(prod, qty=4500, start_date="2026-09-28", freq=Weeks(1))


def test_mts_incompatible_measure_raises_unit_error():
    prod, _, _ = _simple_product()

    with pytest.raises(UnitError, match="invalid measure"):
        MadeToStock(prod, qty=Litre(5), start_date="2026-09-28", freq=Weeks(1))


def test_mts_dates_are_start_of_day_and_end_optional():
    prod, _, _ = _simple_product()

    with_end = MadeToStock(
        prod,
        qty=Unit(1),
        start_date="2026-09-28 13:00:00",
        end_date="2026-10-02 09:30:00",
    )
    no_end = MadeToStock(
        prod, qty=Unit(1), start_date="2026-09-28", freq=Weeks(1)
    )

    assert with_end.start_date == dt.datetime(2026, 9, 28)
    assert with_end.end_date == dt.datetime(2026, 10, 2)
    assert no_end.end_date is None


def test_mts_keeps_custom_unit_qty_unresolved():
    prod, _, _ = _simple_product()
    Case = CustomUnit("Ctrl MTS Case", base_dimension=BaseUnit)
    Case.size_for(prod, Unit(24))

    mts = MadeToStock(
        prod, qty=Case(3), start_date="2026-09-28", freq=Weeks(1)
    )

    # Stored as given; resolved per product at build time
    assert mts.qty.unit is Case
    assert mts.qty.qty == 3


def test_mts_product_group_validates_every_member():
    prod_a, _, _ = _simple_product("Ctrl Grp A")
    prod_b, _, _ = _simple_product("Ctrl Grp B")
    group = ProductGroup("Ctrl Group", products=[prod_a, prod_b])

    Case = CustomUnit("Ctrl Grp Case", base_dimension=BaseUnit)
    Case.size_for(prod_a, Unit(10))  # not sized for prod_b

    with pytest.raises(UnitError, match="has not been sized for Ctrl Grp B"):
        MadeToStock(group, qty=Case(1), start_date="2026-09-28", freq=Weeks(1))


def test_mts_accepts_hard_constraint():
    prod, _, _ = _simple_product()
    MadeToStock(
        prod,
        qty=Unit(1),
        start_date="2026-09-28",
        freq=Weeks(1),
        hard_constraints=MinProductionTime(Hours(4)),
    )


# ===========================================================================
# DemandForecast - adding orders and MTS
# ===========================================================================


def test_forecast_constructor_accepts_single_and_lists():
    prod_a, _, _ = _simple_product("Ctrl A")
    prod_b, _, _ = _simple_product("Ctrl B")
    o1 = Order(due_date="2026-10-06", name="Ctrl O1")
    o2 = Order(due_date="2026-10-06", name="Ctrl O2")
    m1 = MadeToStock(prod_a, Unit(1), "2026-09-28", freq=Weeks(1))
    m2 = MadeToStock(prod_b, Unit(1), "2026-09-28", freq=Weeks(1))

    single = DemandForecast(orders=o1, mts=m1)
    many = DemandForecast(orders=[o1, o2], mts=[m1, m2])

    assert single.orders == [o1] and single.mts == [m1]
    assert many.orders == [o1, o2] and many.mts == [m1, m2]


@pytest.mark.parametrize("bad", [["not an order"], [object()]])
def test_add_order_rejects_non_order(bad):
    forecast = DemandForecast()

    with pytest.raises(TypeError, match="Invalid Order type"):
        forecast.add_order(bad)


def test_add_order_rejects_mixed_list_without_adding_any():
    forecast = DemandForecast()
    order = Order(due_date="2026-10-06", name="Ctrl Mixed")

    with pytest.raises(TypeError, match="Invalid Order type"):
        forecast.add_order([order, "not an order"])

    assert forecast.orders == []


@pytest.mark.parametrize("bad", [["not an mts"], [object()]])
def test_add_mts_rejects_non_mts(bad):
    forecast = DemandForecast()

    with pytest.raises(TypeError, match="Invalid MadeToStock type"):
        forecast.add_mts(bad)


def test_add_same_order_twice_raises():
    forecast = DemandForecast()
    order = Order(due_date="2026-10-06", name="Ctrl Dup Order")
    forecast.add_order(order)

    with pytest.raises(ValueError, match="Cannot add the same order"):
        forecast.add_order(order)


def test_add_same_mts_twice_raises():
    prod, _, _ = _simple_product()
    forecast = DemandForecast()
    mts = MadeToStock(prod, Unit(1), "2026-09-28", freq=Weeks(1))
    forecast.add_mts(mts)

    with pytest.raises(ValueError, match="Cannot raise this MTS order twice"):
        forecast.add_mts(mts)


def test_second_mts_for_same_product_raises():
    prod, _, _ = _simple_product()
    forecast = DemandForecast()
    forecast.add_mts(MadeToStock(prod, Unit(1), "2026-09-28", freq=Weeks(1)))

    with pytest.raises(ValueError, match="Cannot make a second MTS order"):
        forecast.add_mts(
            MadeToStock(prod, Unit(2), "2026-09-28", freq=Weeks(2))
        )


def test_group_mts_overlapping_product_mts_raises():
    prod_a, _, _ = _simple_product("Ctrl Grp A")
    prod_b, _, _ = _simple_product("Ctrl Grp B")
    group = ProductGroup("Ctrl Overlap Group", products=[prod_a, prod_b])
    forecast = DemandForecast()
    forecast.add_mts(MadeToStock(prod_a, Unit(1), "2026-09-28", freq=Weeks(1)))

    with pytest.raises(ValueError, match="Cannot make a second MTS order"):
        forecast.add_mts(
            MadeToStock(group, Unit(1), "2026-09-28", freq=Weeks(1))
        )


# ===========================================================================
# DemandForecast._build - control flow
# ===========================================================================


def test_build_with_no_demand_leaves_buckets_empty():
    forecast = DemandForecast()
    forecast._build(_one_week_problem())

    assert forecast._prod_demand_buckets == {}
    assert forecast._cons_demand_buckets == {}


def test_build_demand_arrays_cover_whole_problem():
    problem = _one_week_problem()
    prod, sub, cons = _simple_product(sub_name="Ctrl Sub", cons_name="Ctrl C")
    order = Order(
        due_date="2026-10-03", name="Ctrl O", lines=Orderline(prod, Unit(10))
    )
    forecast = DemandForecast(orders=order)
    forecast._build(problem)

    for arr in (
        forecast._prod_demand_buckets[prod._id],
        forecast._prod_demand_buckets[sub._id],
        forecast._cons_demand_buckets[cons._id],
    ):
        assert arr.shape == (7 * BUCKETS_PER_DAY,)


def test_order_due_before_problem_start_is_ignored():
    problem = _one_week_problem()
    prod, _, cons = _simple_product(cons_name="Ctrl C")
    order = Order(
        due_date="2026-09-20", name="Ctrl Past", lines=Orderline(prod, Unit(5))
    )
    forecast = DemandForecast(orders=order)
    forecast._build(problem)

    assert prod._id not in forecast._prod_demand_buckets
    assert cons._id not in forecast._cons_demand_buckets


def test_order_production_starting_after_problem_end_is_ignored():
    problem = _one_week_problem()
    prod, _, _ = _simple_product()
    # Default 1 week horizon -> production starts 2026-10-13, after the end
    order = Order(
        due_date="2026-10-20",
        name="Ctrl Future",
        lines=Orderline(prod, Unit(5)),
    )
    forecast = DemandForecast(orders=order)
    forecast._build(problem)

    assert prod._id not in forecast._prod_demand_buckets


def test_order_with_no_lines_adds_no_demand():
    forecast = DemandForecast(
        orders=Order(due_date="2026-10-03", name="Ctrl Empty Order")
    )
    forecast._build(_one_week_problem())

    assert forecast._prod_demand_buckets == {}
    assert forecast._cons_demand_buckets == {}


def test_order_lead_time_sets_start_of_demand():
    problem = _one_week_problem()
    prod, _, _ = _simple_product()
    order = Order(
        due_date="2026-10-03",
        name="Ctrl Lead",
        production_lead_time=Days(2),
        lines=Orderline(prod, Unit(100)),
    )
    forecast = DemandForecast(orders=order)
    forecast._build(problem)

    demand = forecast._prod_demand_buckets[prod._id]
    nonzero = np.nonzero(demand)[0]

    # Production from 2026-10-01 (day 3) up to the due date (day 5)
    assert nonzero.min() == 3 * BUCKETS_PER_DAY
    assert nonzero.max() == 5 * BUCKETS_PER_DAY - 1
    assert np.isclose(demand.sum(), 100.0)


def test_two_orders_for_same_product_accumulate():
    problem = _one_week_problem()
    prod, sub, cons = _simple_product(sub_name="Ctrl Sub", cons_name="Ctrl C")
    # Short lead times keep both orders wholly inside the problem window
    orders = [
        Order(
            due_date="2026-10-03",
            name="Ctrl O1",
            production_lead_time=Days(2),
            lines=Orderline(prod, Unit(100)),
        ),
        Order(
            due_date="2026-10-04",
            name="Ctrl O2",
            production_lead_time=Days(2),
            lines=Orderline(prod, Unit(50)),
        ),
    ]
    forecast = DemandForecast(orders=orders)
    forecast._build(problem)

    assert np.isclose(forecast._prod_demand_buckets[prod._id].sum(), 150.0)
    assert np.isclose(forecast._prod_demand_buckets[sub._id].sum(), 150.0)
    assert np.isclose(forecast._cons_demand_buckets[cons._id].sum(), 150.0)


def test_order_with_custom_unit_line_builds_resolved_demand():
    problem = _one_week_problem()
    prod, _, _ = _simple_product()
    Case = CustomUnit("Ctrl Build Case", base_dimension=BaseUnit)
    Case.size_for(prod, Unit(24))
    order = Order(
        due_date="2026-10-03",
        name="Ctrl Cases",
        production_lead_time=Days(2),
        lines=Orderline(prod, Case(5)),
    )
    forecast = DemandForecast(orders=order)
    forecast._build(problem)

    assert np.isclose(forecast._prod_demand_buckets[prod._id].sum(), 120.0)


def test_order_due_at_problem_end_with_short_lead_time():
    problem = _one_week_problem()  # ends 2026-10-05
    prod, _, _ = _simple_product()
    order = Order(
        due_date="2026-10-05",
        name="Ctrl End",
        production_lead_time=Days(1),
        lines=Orderline(prod, Unit(100)),
    )
    forecast = DemandForecast(orders=order)
    forecast._build(problem)

    demand = forecast._prod_demand_buckets[prod._id]
    assert np.isclose(demand.sum(), 100.0)
    assert np.nonzero(demand)[0].min() == 6 * BUCKETS_PER_DAY


def test_order_overrunning_problem_end_with_short_lead_time():
    problem = _one_week_problem()  # ends 2026-10-05
    prod, _, _ = _simple_product()
    # Production 2026-10-03 -> 2026-10-07: half falls inside the problem
    order = Order(
        due_date="2026-10-07",
        name="Ctrl Overrun",
        production_lead_time=Days(4),
        lines=Orderline(prod, Unit(100)),
    )
    forecast = DemandForecast(orders=order)
    forecast._build(problem)

    assert np.isclose(forecast._prod_demand_buckets[prod._id].sum(), 50.0)


def test_mts_starting_after_problem_end_is_ignored():
    problem = _one_week_problem()
    prod, _, _ = _simple_product()
    mts = MadeToStock(prod, Unit(100), "2026-10-12", freq=Weeks(1))
    forecast = DemandForecast(mts=mts)
    forecast._build(problem)

    assert prod._id not in forecast._prod_demand_buckets


def test_mts_ending_before_problem_start_is_ignored():
    problem = _one_week_problem()
    prod, _, _ = _simple_product()
    mts = MadeToStock(prod, Unit(100), "2026-09-14", end_date="2026-09-21")
    forecast = DemandForecast(mts=mts)
    forecast._build(problem)

    assert prod._id not in forecast._prod_demand_buckets


def test_mts_product_group_creates_demand_for_every_member():
    problem = _one_week_problem()
    prod_a, _, _ = _simple_product("Ctrl Grp A")
    prod_b, _, _ = _simple_product("Ctrl Grp B")
    group = ProductGroup("Ctrl MTS Group", products=[prod_a, prod_b])
    mts = MadeToStock(group, Unit(100), "2026-09-28", end_date="2026-10-05")
    forecast = DemandForecast(mts=mts)
    forecast._build(problem)

    assert np.isclose(forecast._prod_demand_buckets[prod_a._id].sum(), 100.0)
    assert np.isclose(forecast._prod_demand_buckets[prod_b._id].sum(), 100.0)


def test_mts_product_group_custom_unit_resolves_per_member():
    problem = _one_week_problem()
    prod_a, _, _ = _simple_product("Ctrl Grp A")
    prod_b, _, _ = _simple_product("Ctrl Grp B")
    group = ProductGroup("Ctrl Case Group", products=[prod_a, prod_b])
    Case = CustomUnit("Ctrl Grp Case", base_dimension=BaseUnit)
    Case.size_for(prod_a, Unit(10))
    Case.size_for(prod_b, Unit(25))

    mts = MadeToStock(group, Case(4), "2026-09-28", end_date="2026-10-05")
    forecast = DemandForecast(mts=mts)
    forecast._build(problem)

    assert np.isclose(forecast._prod_demand_buckets[prod_a._id].sum(), 40.0)
    assert np.isclose(forecast._prod_demand_buckets[prod_b._id].sum(), 100.0)


def test_mts_products_sharing_consumable_accumulate():
    problem = _one_week_problem()
    cons = Consumable("Ctrl Shared Cons", base_dimension=BaseUnit)
    prod_a = ContinuousProduct("Ctrl A", base_dimension=BaseUnit)
    prod_b = ContinuousProduct("Ctrl B", base_dimension=BaseUnit)
    prod_a.add_component(cons, qty=Unit(1), per=Unit(1))
    prod_b.add_component(cons, qty=Unit(2), per=Unit(1))
    forecast = DemandForecast(
        mts=[
            MadeToStock(prod_a, Unit(100), "2026-09-28", "2026-10-05"),
            MadeToStock(prod_b, Unit(100), "2026-09-28", "2026-10-05"),
        ]
    )
    forecast._build(problem)

    assert np.isclose(forecast._cons_demand_buckets[cons._id].sum(), 300.0)


def test_order_and_mts_for_same_product_accumulate():
    problem = _one_week_problem()
    prod, _, cons = _simple_product(cons_name="Ctrl C")
    forecast = DemandForecast(
        orders=Order(
            due_date="2026-10-05",
            name="Ctrl O",
            lines=Orderline(prod, Unit(100)),
        ),
        mts=MadeToStock(prod, Unit(100), "2026-09-28", end_date="2026-10-05"),
    )
    forecast._build(problem)

    assert np.isclose(forecast._prod_demand_buckets[prod._id].sum(), 200.0)
    assert np.isclose(forecast._cons_demand_buckets[cons._id].sum(), 200.0)


def test_mts_products_sharing_subproduct_accumulate():
    problem = _one_week_problem()
    sub = ContinuousProduct("Ctrl Shared Sub", base_dimension=BaseUnit)
    prod_a = ContinuousProduct("Ctrl A", base_dimension=BaseUnit)
    prod_b = ContinuousProduct("Ctrl B", base_dimension=BaseUnit)
    prod_a.add_component(sub, qty=Unit(1), per=Unit(1))
    prod_b.add_component(sub, qty=Unit(1), per=Unit(1))
    forecast = DemandForecast(
        mts=[
            MadeToStock(prod_a, Unit(100), "2026-09-28", "2026-10-05"),
            MadeToStock(prod_b, Unit(100), "2026-09-28", "2026-10-05"),
        ]
    )
    forecast._build(problem)

    assert np.isclose(forecast._prod_demand_buckets[sub._id].sum(), 200.0)


def test_order_and_mts_sharing_subproduct_accumulate():
    problem = _one_week_problem()
    prod, sub, _ = _simple_product(sub_name="Ctrl Sub")
    forecast = DemandForecast(
        orders=Order(
            due_date="2026-10-05",
            name="Ctrl O",
            lines=Orderline(prod, Unit(100)),
        ),
        mts=MadeToStock(prod, Unit(100), "2026-09-28", end_date="2026-10-05"),
    )
    forecast._build(problem)

    assert np.isclose(forecast._prod_demand_buckets[sub._id].sum(), 200.0)


# ===========================================================================
# Half-open production windows and bucket indices
# ===========================================================================
#
# One week problem: day 0 = 2026-09-28, day 7 = 2026-10-05 (the problem end,
# exclusive). Day 6 (2026-10-04) is the last day of production.


def _nonzero_days(demand):
    """(first day, end day) of the non-zero buckets, end exclusive."""
    nonzero = np.nonzero(demand)[0]
    first = nonzero.min() / BUCKETS_PER_DAY
    end = (nonzero.max() + 1) / BUCKETS_PER_DAY
    return first, end


def test_order_due_on_last_problem_day_gets_no_production_that_day():
    problem = _one_week_problem()
    prod, _, _ = _simple_product()
    order = Order(
        due_date="2026-10-04",
        name="Ctrl Last Day",
        production_lead_time=Days(2),
        lines=Orderline(prod, Unit(100)),
    )
    forecast = DemandForecast(orders=order)
    forecast._build(problem)

    demand = forecast._prod_demand_buckets[prod._id]
    assert _nonzero_days(demand) == (4, 6)
    assert np.isclose(demand.sum(), 100.0)


def test_order_running_past_problem_end_uses_last_day():
    problem = _one_week_problem()
    prod, _, _ = _simple_product()
    order = Order(
        due_date="2026-10-06",
        name="Ctrl Past End",
        production_lead_time=Days(2),
        lines=Orderline(prod, Unit(100)),
    )
    forecast = DemandForecast(orders=order)
    forecast._build(problem)

    demand = forecast._prod_demand_buckets[prod._id]
    # Window 2026-10-04 -> 2026-10-06: only 2026-10-04 is in the problem
    assert _nonzero_days(demand) == (6, 7)
    assert np.isclose(demand.sum(), 50.0)


def test_order_lead_longer_than_problem_spans_whole_problem():
    problem = _one_week_problem()
    prod, _, _ = _simple_product()
    order = Order(
        due_date="2026-10-07",
        name="Ctrl Long Lead",
        production_lead_time=Days(10),
        lines=Orderline(prod, Unit(100)),
    )
    forecast = DemandForecast(orders=order)
    forecast._build(problem)

    demand = forecast._prod_demand_buckets[prod._id]
    assert _nonzero_days(demand) == (0, 7)
    assert np.isclose(demand.sum(), 70.0)


def test_order_due_on_problem_start_is_ignored():
    problem = _one_week_problem()
    prod, _, _ = _simple_product()
    order = Order(
        due_date="2026-09-28",
        name="Ctrl Due At Start",
        lines=Orderline(prod, Unit(100)),
    )
    forecast = DemandForecast(orders=order)
    forecast._build(problem)

    assert prod._id not in forecast._prod_demand_buckets


def test_order_production_starting_at_problem_end_is_ignored():
    problem = _one_week_problem()
    prod, _, _ = _simple_product()
    order = Order(
        due_date="2026-10-07",
        name="Ctrl Starts At End",
        production_lead_time=Days(2),
        lines=Orderline(prod, Unit(100)),
    )
    forecast = DemandForecast(orders=order)
    forecast._build(problem)

    assert prod._id not in forecast._prod_demand_buckets


def test_two_lines_for_same_product_accumulate_demand():
    problem = _one_week_problem()
    prod, _, cons = _simple_product(cons_name="Ctrl C")
    order = Order(
        due_date="2026-10-03",
        name="Ctrl Two Lines Build",
        production_lead_time=Days(2),
        lines=[Orderline(prod, Unit(60)), Orderline(prod, Unit(40))],
    )
    forecast = DemandForecast(orders=order)
    forecast._build(problem)

    assert np.isclose(forecast._prod_demand_buckets[prod._id].sum(), 100.0)
    assert np.isclose(forecast._cons_demand_buckets[cons._id].sum(), 100.0)


@pytest.mark.parametrize("lead", [Days(0), Days(-1)])
def test_order_non_positive_lead_time_raises(lead):
    with pytest.raises(ValueError, match="lead time must be positive"):
        Order(
            due_date="2026-10-03",
            name="Ctrl Bad Lead",
            production_lead_time=lead,
        )


@pytest.mark.parametrize("freq", [Days(0), Days(-2)])
def test_mts_non_positive_freq_raises(freq):
    prod, _, _ = _simple_product()

    with pytest.raises(ValueError, match="frequency must be positive"):
        MadeToStock(prod, Unit(1), start_date="2026-09-28", freq=freq)


def test_mts_starting_mid_problem_cycles_from_its_own_start():
    problem = _one_week_problem()
    prod, _, _ = _simple_product()
    # Cycles 09-30..10-02, 10-02..10-04, 10-04..10-06 (half inside)
    mts = MadeToStock(prod, Unit(100), start_date="2026-09-30", freq=Days(2))
    forecast = DemandForecast(mts=mts)
    forecast._build(problem)

    demand = forecast._prod_demand_buckets[prod._id]
    assert _nonzero_days(demand) == (2, 7)
    assert np.isclose(demand.sum(), 250.0)


def test_mts_cycle_longer_than_problem_started_before():
    problem = _one_week_problem()
    prod, _, _ = _simple_product()
    # One cycle 09-21..10-12; 7 of its 21 days are in the problem
    mts = MadeToStock(prod, Unit(300), start_date="2026-09-21", freq=Weeks(3))
    forecast = DemandForecast(mts=mts)
    forecast._build(problem)

    demand = forecast._prod_demand_buckets[prod._id]
    assert _nonzero_days(demand) == (0, 7)
    assert np.isclose(demand.sum(), 100.0)


def test_mts_long_cycle_starting_mid_problem_is_pro_rata():
    problem = _one_week_problem()
    prod, _, _ = _simple_product()
    # One cycle 10-01..10-15; 4 of its 14 days are in the problem
    mts = MadeToStock(prod, Unit(140), start_date="2026-10-01", freq=Weeks(2))
    forecast = DemandForecast(mts=mts)
    forecast._build(problem)

    demand = forecast._prod_demand_buckets[prod._id]
    assert _nonzero_days(demand) == (3, 7)
    assert np.isclose(demand.sum(), 40.0)


def test_mts_cycle_cut_short_by_end_date_makes_full_qty_before_end():
    problem = _one_week_problem()
    prod, _, _ = _simple_product()
    # Cycles 09-28..10-01 and 10-01..10-04, but the MTS ends 10-02: the last
    # cycle is cut to 10-01..10-02 and still makes its full quantity
    mts = MadeToStock(
        prod,
        Unit(100),
        start_date="2026-09-28",
        end_date="2026-10-02",
        freq=Days(3),
    )
    forecast = DemandForecast(mts=mts)
    forecast._build(problem)

    demand = forecast._prod_demand_buckets[prod._id]
    assert _nonzero_days(demand) == (0, 4)
    assert np.isclose(demand.sum(), 200.0)
    assert np.isclose(demand[3 * BUCKETS_PER_DAY :].sum(), 100.0)


def test_mts_one_off_ending_at_problem_start_is_ignored():
    problem = _one_week_problem()
    prod, _, _ = _simple_product()
    mts = MadeToStock(
        prod, Unit(100), start_date="2026-09-21", end_date="2026-09-28"
    )
    forecast = DemandForecast(mts=mts)
    forecast._build(problem)

    assert prod._id not in forecast._prod_demand_buckets


def test_mts_starting_at_problem_end_is_ignored():
    problem = _one_week_problem()
    prod, _, _ = _simple_product()
    forecast = DemandForecast(
        mts=[
            MadeToStock(prod, Unit(100), "2026-10-05", end_date="2026-10-08"),
        ]
    )
    forecast._build(problem)

    assert prod._id not in forecast._prod_demand_buckets


def test_mts_recurring_starting_at_problem_end_is_ignored():
    problem = _one_week_problem()
    prod, _, _ = _simple_product()
    forecast = DemandForecast(
        mts=MadeToStock(prod, Unit(100), "2026-10-05", freq=Weeks(1))
    )
    forecast._build(problem)

    assert prod._id not in forecast._prod_demand_buckets
