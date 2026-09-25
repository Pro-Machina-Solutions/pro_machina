import warnings
from decimal import Decimal

import pytest

from pro_machina.durations import Hours
from pro_machina.exceptions import ProductError, UnitError
from pro_machina.measures import CustomUnit, Kilo, Litre, Volume, Weight
from pro_machina.problem import (
    BatchProduct,
    Consumable,
    ContinuousProduct,
    ProductGroup,
)
from pro_machina.problem.hard_constraints import (
    MinProductionTime,
    SeasonalProduction,
)

# ===========================================================================
# Scope
# ===========================================================================
#
# BatchProduct/BatchMachine are unfinished (e.g. BatchProduct doesn't accept
# `code` and never initialises `_batches`) and SoftConstraint has no
# concrete, instantiable implementation anywhere in the codebase at the time
# of writing (OverstockingPenalty does not implement the abstract
# `_set_level` method). Both are out of scope for this module and are
# deliberately not exercised here.

# ===========================================================================
# Product creation & identity
# ===========================================================================


def test_continuous_product_creation_sets_expected_defaults():
    prod = ContinuousProduct("TP Continuous Defaults", base_dimension=Weight)

    assert prod.name == "TP Continuous Defaults"
    assert prod.code == ""
    assert prod.base_dimension is Weight


def test_continuous_product_code_is_stored():
    # Regression test: ContinuousProduct.__init__ used to silently drop the
    # `code` argument instead of passing it through to _Product.__init__.
    prod = ContinuousProduct(
        "TP Continuous Code", base_dimension=Weight, code="ABC123"
    )

    assert prod.code == "ABC123"


def test_product_ids_increment():
    prod_a = ContinuousProduct("TP Ids A", base_dimension=Weight)
    prod_b = ContinuousProduct("TP Ids B", base_dimension=Weight)

    assert prod_b._id == prod_a._id + 1


def test_duplicate_name_and_code_raises_product_error():
    ContinuousProduct("TP Dup Name", base_dimension=Weight, code="X1")

    with pytest.raises(
        ProductError,
        match="Name and code combinations for products must be unique",
    ):
        ContinuousProduct("TP Dup Name", base_dimension=Weight, code="X1")


def test_duplicate_name_different_code_is_allowed():
    ContinuousProduct("TP Same Name", base_dimension=Weight, code="Y1")
    # Should not raise - different code disambiguates
    ContinuousProduct("TP Same Name", base_dimension=Weight, code="Y2")


# ===========================================================================
# add_component - consumables
# ===========================================================================


def test_add_component_consumable_computes_base_ratio():
    sugar = Consumable("TP Cons Sugar 1", base_dimension=Weight)
    prod = ContinuousProduct("TP Prod Cons 1", base_dimension=Weight)

    prod.add_component(sugar, qty=Kilo("0.5"), per=Kilo(1))

    assert len(prod._consumables) == 1
    entry = prod._consumables[0]
    assert entry["item"] is sugar
    assert entry["qty"] == Decimal("0.5")
    # `unit` is the symbol of the *base* unit for the dimension (grams),
    # not the unit the caller specified the quantity in (kilos).
    assert entry["unit"] == "g"


def test_add_component_consumable_updates_bom():
    sugar = Consumable("TP Cons Sugar 2", base_dimension=Weight)
    prod = ContinuousProduct("TP Prod Cons 2", base_dimension=Weight)

    prod.add_component(sugar, qty=Kilo("0.5"), per=Kilo(1))

    assert prod._bom_consumables == {sugar._id: Decimal("0.5")}
    assert prod._bom_products == {}


def test_add_component_returns_self_for_chaining():
    sugar = Consumable("TP Cons Chain", base_dimension=Weight)
    flour = Consumable("TP Cons Chain 2", base_dimension=Weight)
    prod = ContinuousProduct("TP Prod Chain", base_dimension=Weight)

    result = prod.add_component(sugar, qty=Kilo(1), per=Kilo(1)).add_component(
        flour, qty=Kilo(1), per=Kilo(1)
    )

    assert result is prod
    assert len(prod._consumables) == 2


def test_add_component_duplicate_consumable_raises_product_error():
    sugar = Consumable("TP Cons Dup", base_dimension=Weight)
    prod = ContinuousProduct("TP Prod Dup Cons", base_dimension=Weight)
    prod.add_component(sugar, qty=Kilo(1), per=Kilo(1))

    with pytest.raises(ProductError, match="cannot be added twice"):
        prod.add_component(sugar, qty=Kilo(1), per=Kilo(1))


def test_add_component_incompatible_per_unit_raises_unit_error():
    cons = Consumable("TP Cons Per Err", base_dimension=Weight)
    prod = ContinuousProduct("TP Prod Per Err", base_dimension=Weight)

    with pytest.raises(UnitError, match="invalid measure for TP Prod Per Err"):
        prod.add_component(cons, qty=Kilo(1), per=Litre(1))


def test_add_component_incompatible_component_unit_raises_unit_error():
    cons = Consumable("TP Cons Unit Err", base_dimension=Volume)
    prod = ContinuousProduct("TP Prod Unit Err", base_dimension=Weight)

    with pytest.raises(
        UnitError, match="invalid measure for TP Cons Unit Err"
    ):
        prod.add_component(cons, qty=Kilo(1), per=Kilo(1))


# ===========================================================================
# add_component - subproducts and BOM hoisting
# ===========================================================================


def test_add_component_subproduct_updates_bom_products():
    sub = ContinuousProduct("TP Sub 1", base_dimension=Weight)
    top = ContinuousProduct("TP Top 1", base_dimension=Weight)

    top.add_component(sub, qty=Kilo(2), per=Kilo(1))

    assert top._bom_products == {sub._id: Decimal("2")}
    assert len(top._products) == 1
    assert top._products[0]["item"] is sub


def test_add_component_subproduct_hoists_nested_consumables():
    flour = Consumable("TP Cons Hoist", base_dimension=Weight)
    sub = ContinuousProduct("TP Sub Hoist", base_dimension=Weight)
    sub.add_component(flour, qty=Kilo(1), per=Kilo(1))  # 1.0 flour per kg sub

    top = ContinuousProduct("TP Top Hoist", base_dimension=Weight)
    top.add_component(sub, qty=Kilo(2), per=Kilo(1))  # 2.0 sub per kg top

    # top uses 2 sub per kg, each sub needs 1 flour per kg -> 2 flour per kg
    assert top._bom_consumables == {flour._id: Decimal("2")}


def test_add_component_bom_cascades_through_multiple_levels():
    flour = Consumable("TP Cons Cascade", base_dimension=Weight)

    grandchild = ContinuousProduct("TP Grandchild", base_dimension=Weight)
    grandchild.add_component(flour, qty=Kilo(1), per=Kilo(1))

    child = ContinuousProduct("TP Child", base_dimension=Weight)
    child.add_component(grandchild, qty=Kilo(2), per=Kilo(1))

    parent = ContinuousProduct("TP Parent", base_dimension=Weight)
    parent.add_component(child, qty=Kilo(3), per=Kilo(1))

    assert parent._bom_products == {
        child._id: Decimal("3"),
        grandchild._id: Decimal("6"),
    }
    assert parent._bom_consumables == {flour._id: Decimal("6")}


def test_add_component_duplicate_subproduct_raises_product_error():
    sub = ContinuousProduct("TP Sub Dup", base_dimension=Weight)
    top = ContinuousProduct("TP Top Dup", base_dimension=Weight)
    top.add_component(sub, qty=Kilo(1), per=Kilo(1))

    with pytest.raises(ProductError, match="cannot be added twice"):
        top.add_component(sub, qty=Kilo(1), per=Kilo(1))


# ===========================================================================
# add_component - custom units
# ===========================================================================


def test_add_component_custom_unit_computes_correct_ratio():
    sugar = Consumable("TP Cons Custom Unit", base_dimension=Weight)
    Bag = CustomUnit("TP Bag", dimension=Weight)
    Bag.size_for(sugar, Kilo("0.25"))

    prod = ContinuousProduct("TP Prod Custom Unit", base_dimension=Weight)
    prod.add_component(sugar, qty=Bag(2), per=Kilo(1))

    # 2 bags * 0.25kg = 0.5kg, per 1kg -> ratio of 0.5
    assert prod._bom_consumables == {sugar._id: Decimal("0.50")}


def test_add_component_custom_unit_not_sized_raises_unit_error():
    sugar = Consumable("TP Cons Custom Unsized", base_dimension=Weight)
    Box = CustomUnit("TP Box", dimension=Weight)
    prod = ContinuousProduct("TP Prod Custom Unsized", base_dimension=Weight)

    with pytest.raises(UnitError, match="has not been sized for"):
        prod.add_component(sugar, qty=Box(1), per=Kilo(1))


# ===========================================================================
# add_hard_constraint
# ===========================================================================


def test_add_hard_constraint_single():
    prod = ContinuousProduct("TP HC Single", base_dimension=Weight)
    con = MinProductionTime(Hours(4))

    prod.add_hard_constraint(con)

    assert prod._hard_constraints == [con]
    assert con.product is prod


def test_add_hard_constraint_list():
    prod = ContinuousProduct("TP HC List", base_dimension=Weight)
    con_a = MinProductionTime(
        Hours(4), start_date="2026-01-01", end_date="2026-01-05"
    )
    con_b = SeasonalProduction(start_date="2026-02-01", end_date="2026-02-05")

    prod.add_hard_constraint([con_a, con_b])

    assert prod._hard_constraints == [con_a, con_b]


def test_add_hard_constraint_wrong_type_raises_type_error():
    prod = ContinuousProduct("TP HC Type Err", base_dimension=Weight)

    with pytest.raises(TypeError, match="must all be of type HardConstraint"):
        prod.add_hard_constraint("not a constraint")


# ===========================================================================
# Hard constraint collision detection
# ===========================================================================


def test_collision_both_whole_duration_warns():
    prod = ContinuousProduct("TP Coll Both Whole", base_dimension=Weight)
    prod.add_hard_constraint(MinProductionTime(Hours(4)))

    with pytest.warns(UserWarning, match="Both constraints span"):
        prod.add_hard_constraint(MinProductionTime(Hours(6)))


def test_collision_old_dated_new_whole_warns():
    prod = ContinuousProduct("TP Coll Old Dated", base_dimension=Weight)
    prod.add_hard_constraint(
        MinProductionTime(
            Hours(4), start_date="2026-01-01", end_date="2026-01-10"
        )
    )

    with pytest.warns(
        UserWarning, match="new constraint spans the whole problem duration"
    ):
        prod.add_hard_constraint(MinProductionTime(Hours(6)))


def test_collision_old_whole_new_dated_warns():
    prod = ContinuousProduct("TP Coll Old Whole", base_dimension=Weight)
    prod.add_hard_constraint(MinProductionTime(Hours(4)))

    with pytest.warns(
        UserWarning, match="old constraint spans the whole problem duration"
    ):
        prod.add_hard_constraint(
            MinProductionTime(
                Hours(6), start_date="2026-01-01", end_date="2026-01-10"
            )
        )


def test_collision_overlapping_dates_warns_with_correct_range():
    prod = ContinuousProduct("TP Coll Overlap", base_dimension=Weight)
    prod.add_hard_constraint(
        SeasonalProduction(start_date="2026-01-01", end_date="2026-01-10")
    )

    with pytest.warns(
        UserWarning,
        match=r"dates between 2026-01-05 and 2026-01-10",
    ):
        prod.add_hard_constraint(
            SeasonalProduction(start_date="2026-01-05", end_date="2026-01-20")
        )


def test_collision_non_overlapping_dates_does_not_warn():
    prod = ContinuousProduct("TP Coll No Overlap", base_dimension=Weight)
    prod.add_hard_constraint(
        SeasonalProduction(start_date="2026-01-01", end_date="2026-01-10")
    )

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        prod.add_hard_constraint(
            SeasonalProduction(start_date="2026-03-01", end_date="2026-03-10")
        )

    assert caught == []


def test_collision_silenced_by_option(monkeypatch):
    import pro_machina

    monkeypatch.setitem(
        pro_machina.options, "silence_constraint_overrides", True
    )

    prod = ContinuousProduct("TP Coll Silenced", base_dimension=Weight)
    prod.add_hard_constraint(MinProductionTime(Hours(4)))

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        prod.add_hard_constraint(MinProductionTime(Hours(6)))

    assert caught == []


def test_collision_only_applies_to_same_constraint_type():
    prod = ContinuousProduct("TP Coll Diff Type", base_dimension=Weight)
    prod.add_hard_constraint(MinProductionTime(Hours(4)))

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        prod.add_hard_constraint(
            SeasonalProduction(start_date="2026-01-01", end_date="2026-01-02")
        )

    assert caught == []
    assert len(prod._hard_constraints) == 2


# ===========================================================================
# ProductGroup
# ===========================================================================


def test_group_init_empty():
    group = ProductGroup("TP Group Empty")

    assert group._products == {}


def test_group_init_with_products():
    prod_a = ContinuousProduct("TP Group Init A", base_dimension=Weight)
    prod_b = ContinuousProduct("TP Group Init B", base_dimension=Weight)

    group = ProductGroup("TP Group Init", [prod_a, prod_b])

    assert set(group._products.values()) == {prod_a, prod_b}


def test_group_init_wrong_type_raises_type_error():
    with pytest.raises(
        TypeError, match="Invalid Product subtype added to group."
    ):
        ProductGroup("TP Group Bad Init", ["not a product"])


def test_group_init_duplicate_raises_product_error():
    prod = ContinuousProduct("TP Group Dup Init", base_dimension=Weight)

    with pytest.raises(ProductError, match="Duplicate product in grouping"):
        ProductGroup("TP Group Dup", [prod, prod])


def test_group_add_products_single_and_list():
    group = ProductGroup("TP Group Add")
    prod_a = ContinuousProduct("TP Group Add A", base_dimension=Weight)
    prod_b = ContinuousProduct("TP Group Add B", base_dimension=Weight)
    prod_c = ContinuousProduct("TP Group Add C", base_dimension=Weight)

    group.add_products(prod_a)
    group.add_products([prod_b, prod_c])

    assert set(group._products.values()) == {prod_a, prod_b, prod_c}


def test_group_add_products_wrong_type_raises_type_error():
    # Regression test: add_products used to check for duplicates before
    # checking types, so a non-Product item raised AttributeError instead
    # of the documented TypeError.
    group = ProductGroup("TP Group Add Bad Type")

    with pytest.raises(TypeError, match="Invalid Product subtype"):
        group.add_products(["not a product"])


def test_group_add_products_duplicate_raises_product_error():
    prod = ContinuousProduct("TP Group Add Dup", base_dimension=Weight)
    group = ProductGroup("TP Group Add Dup Grp", [prod])

    with pytest.raises(ProductError, match="Duplicate product added"):
        group.add_products(prod)


def test_group_add_component_delegates_to_all_products():
    prod_a = ContinuousProduct("TP Group Comp A", base_dimension=Weight)
    prod_b = ContinuousProduct("TP Group Comp B", base_dimension=Weight)
    group = ProductGroup("TP Group Comp", [prod_a, prod_b])
    cons = Consumable("TP Group Comp Cons", base_dimension=Weight)

    group.add_component(cons, qty=Kilo(1), per=Kilo(1))

    assert prod_a._bom_consumables == {cons._id: Decimal("1")}
    assert prod_b._bom_consumables == {cons._id: Decimal("1")}


def test_group_add_hard_constraint_applies_to_all_products():
    prod_a = ContinuousProduct("TP Group HC A", base_dimension=Weight)
    prod_b = ContinuousProduct("TP Group HC B", base_dimension=Weight)
    group = ProductGroup("TP Group HC", [prod_a, prod_b])
    con = SeasonalProduction(start_date="2026-01-01", end_date="2026-01-10")

    group.add_hard_constraint(con)

    assert prod_a._hard_constraints == [con]
    assert prod_b._hard_constraints == [con]


def test_group_add_hard_constraint_wrong_type_raises_type_error():
    group = ProductGroup("TP Group HC Type Err")

    with pytest.raises(TypeError, match="must all be of type HardConstraint"):
        group.add_hard_constraint("not a constraint")


def test_get_prod_by_name_returns_product():
    prod = ContinuousProduct("TP Get By Name", base_dimension=Weight)
    group = ProductGroup("TP Get Group", [prod])

    assert group.get_prod_by_name("TP Get By Name") is prod


def test_get_prod_by_name_with_code_disambiguates():
    prod_uk = ContinuousProduct(
        "TP Get Dupe Name", base_dimension=Weight, code="UK"
    )
    prod_us = ContinuousProduct(
        "TP Get Dupe Name", base_dimension=Weight, code="US"
    )
    group = ProductGroup("TP Get Group 2", [prod_uk, prod_us])

    assert group.get_prod_by_name("TP Get Dupe Name", "UK") is prod_uk
    assert group.get_prod_by_name("TP Get Dupe Name", "US") is prod_us


def test_get_prod_by_name_missing_raises_value_error():
    group = ProductGroup("TP Get Group Missing")

    with pytest.raises(ValueError, match="Product name not recognised"):
        group.get_prod_by_name("TP Nonexistent")


def test_cannot_make_product_group_of_mixed_types():
    cont = ContinuousProduct("Test Cont", base_dimension=Weight)
    batch = BatchProduct("Test Batch", base_dimension=Weight)

    with pytest.raises(
        TypeError, match="Groups must contain the same product types"
    ):
        group = ProductGroup("Added to together", products=[cont, batch])

    group = ProductGroup("Attempt mixed added to in parts")
    group.add_products(cont)

    with pytest.raises(
        TypeError, match="Groups must contain the same product types"
    ):
        group.add_products(batch)
