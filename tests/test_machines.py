import warnings

import numpy as np
import pytest

from pro_machina.durations import Hours, Mins
from pro_machina.exceptions import (
    MachineError,
    ShiftDefinitionError,
    UnitError,
)
from pro_machina.measures import (
    BaseUnit,
    CustomUnit,
    Litre,
    Unit,
    _UnitRegistry,
)
from pro_machina.problem import (
    ContinuousMachine,
    ContinuousProduct,
    ProductGroup,
)
from pro_machina.problem._constraints import ConstraintLevel
from pro_machina.problem.hard_constraints import MinProductionTime
from pro_machina.problem.machines import ContinuousMachineGroup
from pro_machina.util import (
    Singleton,
    as_day_end,
    as_day_start,
    get_bucket_index,
)

# ===========================================================================
# Scope
# ===========================================================================
#
# BatchMachine is commented out/unimplemented in machines.py (and the
# `batch_machine` fixture in conftest.py references it but is unusable), so
# it - along with anything BatchProduct-related - is deliberately out of
# scope here. SoftConstraint has no concrete, instantiable implementation
# anywhere in the codebase at the time of writing, so it is also out of
# scope.

# ===========================================================================
# Machine creation & identity
# ===========================================================================


def test_continuous_machine_creation_sets_expected_defaults():
    mach = ContinuousMachine("TM Defaults")

    assert mach.name == "TM Defaults"
    assert mach.default_run_rate is None
    assert mach.default_per is None
    assert mach._products == {}
    assert mach._shifts == []
    assert mach._hard_constraints == []
    assert mach._soft_constraints == []


def test_continuous_machine_creation_stores_optional_defaults():
    run_rate = Unit(10)
    per = Mins(1)
    mach = ContinuousMachine(
        "TM With Defaults", default_run_rate=run_rate, default_per=per
    )

    # Stored as-is, not copied or transformed.
    assert mach.default_run_rate is run_rate
    assert mach.default_per is per


def test_machine_ids_increment():
    mach_a = ContinuousMachine("TM Ids A")
    mach_b = ContinuousMachine("TM Ids B")

    assert mach_b._id == mach_a._id + 1


# ===========================================================================
# add_shift / clear_shifts
# ===========================================================================


def test_add_shift_stores_entry(cont_machine, simple_shift):
    cont_machine.add_shift(simple_shift, start_date="2026-10-01")

    assert len(cont_machine._shifts) == 1
    entry = cont_machine._shifts[0]
    assert entry["shift"] is simple_shift
    assert entry["start"] == as_day_start("2026-10-01")
    assert entry["end"] is None


def test_add_shift_end_date_without_start_date_raises(
    cont_machine, simple_shift
):
    with pytest.raises(
        ShiftDefinitionError,
        match="Cannot set an end date without an explicit start date",
    ):
        cont_machine.add_shift(simple_shift, end_date="2026-10-01")


def test_add_shift_wrong_type_raises_type_error(cont_machine):
    with pytest.raises(TypeError, match="Not a valid shift pattern"):
        cont_machine.add_shift("not a shift pattern")


def test_add_shift_end_before_start_raises_value_error(
    cont_machine, simple_shift
):
    with pytest.raises(ValueError, match="End date cannot be before start"):
        cont_machine.add_shift(
            simple_shift, start_date="2026-10-02", end_date="2026-10-01"
        )


def test_clear_shifts_removes_existing_shifts(cont_machine, simple_shift):
    cont_machine.add_shift(simple_shift)
    assert len(cont_machine._shifts) == 1

    cont_machine.clear_shifts()

    assert cont_machine._shifts == []


# ===========================================================================
# _build_shift_productivity
# ===========================================================================
#
# base_problem spans exactly one week (2026-03-02 00:00:00 to 2026-03-09
# 00:00:00) in Mins(15) buckets, i.e. 672 buckets.


def test_shift_productivity_defaults_to_full_output_with_no_shifts(
    base_problem, cont_machine
):
    productivity = cont_machine._build_shift_productivity(base_problem)

    assert len(productivity) == 672
    assert np.all(productivity == 100.0)


def test_shift_productivity_reflects_undated_shift_pattern(
    base_problem, cont_machine, simple_shift
):
    # With no start/end date the shift applies across the whole problem span.
    cont_machine.add_shift(simple_shift)

    productivity = cont_machine._build_shift_productivity(base_problem)

    assert len(productivity) == 672
    assert set(np.unique(productivity)) == {0.0, 100.0}
    # 5 working days x (8hr work period - 30min break) = 37.5hrs of
    # production, in Mins(15) buckets.
    assert np.count_nonzero(productivity) == 150
    assert productivity.sum() == 15000.0


def test_shift_productivity_dated_shift_only_affects_its_window(
    base_problem, cont_machine, simple_shift
):
    cont_machine.add_shift(
        simple_shift, start_date="2026-03-03", end_date="2026-03-05"
    )

    productivity = cont_machine._build_shift_productivity(base_problem)

    start_bucket = get_bucket_index(
        base_problem._start,
        base_problem._end,
        base_problem.config.timebucket,
        as_day_start("2026-03-03"),
    )
    end_bucket = get_bucket_index(
        base_problem._start,
        base_problem._end,
        base_problem.config.timebucket,
        as_day_end("2026-03-05"),
    )

    # Once *any* shift is specified, buckets outside of its window default
    # to zero rather than the "always on" 100 used when there are no shifts
    # at all.
    assert np.all(productivity[:start_bucket] == 0.0)
    assert np.all(productivity[end_bucket:] == 0.0)
    assert np.count_nonzero(
        productivity[start_bucket:end_bucket]
    ) == np.count_nonzero(productivity)
    assert productivity.sum() == 9000.0


def test_shift_productivity_later_dated_shift_overrides_only_its_window(
    base_problem, cont_machine, simple_shift, irregular_shift_pattern
):
    cont_machine.add_shift(simple_shift)
    baseline = cont_machine._build_shift_productivity(base_problem).copy()

    cont_machine.add_shift(
        irregular_shift_pattern,
        start_date="2026-03-03",
        end_date="2026-03-04",
    )
    overridden = cont_machine._build_shift_productivity(base_problem)

    start_bucket = get_bucket_index(
        base_problem._start,
        base_problem._end,
        base_problem.config.timebucket,
        as_day_start("2026-03-03"),
    )
    end_bucket = get_bucket_index(
        base_problem._start,
        base_problem._end,
        base_problem.config.timebucket,
        as_day_end("2026-03-04"),
    )

    assert np.array_equal(baseline[:start_bucket], overridden[:start_bucket])
    assert np.array_equal(baseline[end_bucket:], overridden[end_bucket:])
    assert not np.array_equal(
        baseline[start_bucket:end_bucket],
        overridden[start_bucket:end_bucket],
    )


# ===========================================================================
# add_product - type checks & bookkeeping
# ===========================================================================


def test_add_product_wrong_type_raises_type_error(cont_machine):
    with pytest.raises(
        TypeError, match="Can only add ContinuousProduct to machine"
    ):
        cont_machine.add_product(
            "not a product", run_rate=Unit(10), per=Mins(1)
        )


def test_add_product_duplicate_raises_machine_error(cont_machine):
    prod = ContinuousProduct("AP Duplicate", base_dimension=BaseUnit)
    cont_machine.add_product(prod, run_rate=Unit(10), per=Mins(1))

    with pytest.raises(
        MachineError, match="has already been assigned to machine"
    ):
        cont_machine.add_product(prod, run_rate=Unit(10), per=Mins(1))


def test_add_product_stores_product_run_rate_and_per(cont_machine):
    prod = ContinuousProduct("AP Stores Entry", base_dimension=BaseUnit)

    cont_machine.add_product(prod, run_rate=Unit(10), per=Mins(1))

    entry = cont_machine._products[prod._id]
    assert entry["product"] is prod
    assert entry["run_rate"] is not None
    assert entry["run_rate_per"] is not None


def test_add_product_uses_machine_defaults_when_unspecified():
    run_rate = Unit(10)
    per = Mins(1)
    mach = ContinuousMachine(
        "AP Defaults Mach", default_run_rate=run_rate, default_per=per
    )
    prod = ContinuousProduct("AP Defaults Prod", base_dimension=BaseUnit)

    mach.add_product(prod)

    entry = mach._products[prod._id]
    assert entry["run_rate"] is run_rate
    assert entry["run_rate_per"] is per


def test_add_product_explicit_values_override_machine_defaults():
    mach = ContinuousMachine(
        "AP Override Mach",
        default_run_rate=Unit(5),
        default_per=Mins(5),
    )
    prod = ContinuousProduct("AP Override Prod", base_dimension=BaseUnit)
    run_rate = Unit(99)
    per = Mins(1)

    mach.add_product(prod, run_rate=run_rate, per=per)

    entry = mach._products[prod._id]
    assert entry["run_rate"] is run_rate
    assert entry["run_rate_per"] is per


def test_add_product_missing_run_rate_raises_machine_error(cont_machine):
    prod = ContinuousProduct("AP Missing Run Rate", base_dimension=BaseUnit)

    with pytest.raises(
        MachineError,
        match="Neither a default run rate or a specific run rate",
    ):
        cont_machine.add_product(prod, per=Mins(1))


def test_add_product_missing_per_raises_machine_error(cont_machine):
    prod = ContinuousProduct("AP Missing Per", base_dimension=BaseUnit)

    with pytest.raises(
        MachineError,
        match="Neither a default time period or a specific time period",
    ):
        cont_machine.add_product(prod, run_rate=Unit(10))


def test_add_product_inherits_product_hard_constraints_as_deep_copy(
    cont_machine,
):
    prod = ContinuousProduct("AP Inherit HC", base_dimension=BaseUnit)
    con = MinProductionTime(Hours(4))
    prod.add_hard_constraint(con)

    cont_machine.add_product(prod, run_rate=Unit(10), per=Mins(1))

    assert len(cont_machine._hard_constraints) == 1
    inherited = cont_machine._hard_constraints[0]
    assert isinstance(inherited, MinProductionTime)
    assert inherited is not con
    assert inherited.value == con.value
    # The product's own constraint list is untouched by the copy.
    assert prod._hard_constraints == [con]
    assert prod._hard_constraints[0] is con


# ===========================================================================
# add_product - unit compatibility
# ===========================================================================


def test_add_product_incompatible_base_units_raises_unit_error(cont_machine):
    prod = ContinuousProduct("AP Incompatible", base_dimension=BaseUnit)

    with pytest.raises(UnitError, match="Production units of Litre"):
        cont_machine.add_product(prod, run_rate=Litre(10), per=Mins(1))


def test_add_product_incompatible_default_run_rate_raises_unit_error():
    mach = ContinuousMachine(
        "AP Incompatible Default",
        default_run_rate=Litre(10),
        default_per=Mins(1),
    )
    prod = ContinuousProduct(
        "AP Incompatible Default Prod", base_dimension=BaseUnit
    )

    with pytest.raises(UnitError, match="Production units of Litre"):
        mach.add_product(prod)


def test_add_product_compatible_custom_unit_works(cont_machine):
    Case = CustomUnit("AP Case", dimension=BaseUnit)
    prod = ContinuousProduct("AP Custom Unit Prod", base_dimension=BaseUnit)
    Case.size_for(prod, Unit(10))
    run_rate = Case(2)

    cont_machine.add_product(prod, run_rate=run_rate, per=Mins(1))

    assert cont_machine._products[prod._id]["run_rate"] is run_rate


def test_add_product_custom_unit_not_registered_raises_unit_error(
    cont_machine,
):
    # _UnitRegistry is a process-wide Singleton, and CustomUnit's __eq__ /
    # __hash__ are based purely on the class name rather than identity or
    # `.name` (see measures.py), so every CustomUnit that has ever been
    # registered - by any test, for any name - shares the same entry in the
    # registry. Reset the singleton so "has not been registered" is
    # reachable here regardless of what other tests already registered.
    Singleton._instances.pop(_UnitRegistry, None)

    Case = CustomUnit("AP Unregistered Case", dimension=BaseUnit)
    prod = ContinuousProduct("AP Unregistered Prod", base_dimension=BaseUnit)

    with pytest.raises(UnitError, match="has not been registered"):
        cont_machine.add_product(prod, run_rate=Case(1), per=Mins(1))


def test_add_product_custom_unit_incompatible_with_product_raises_unit_error(
    cont_machine,
):
    # `CustomUnit.size_for()` itself enforces compatibility at registration
    # time, so the only way to reach the incompatibility check inside
    # `add_product()` is to register the sizing directly against the
    # registry, bypassing that guard.
    Case = CustomUnit("AP Mismatched Case", dimension=BaseUnit)
    prod = ContinuousProduct("AP Mismatched Prod", base_dimension=BaseUnit)
    _UnitRegistry().add(Case, prod, Litre(10))

    with pytest.raises(
        UnitError, match="Production units of AP Mismatched Case"
    ):
        cont_machine.add_product(prod, run_rate=Case(1), per=Mins(1))


# ===========================================================================
# add_product_group
# ===========================================================================


def test_add_product_group_wrong_type_raises_type_error(cont_machine):
    with pytest.raises(TypeError, match="Not a valid ProductGroup."):
        cont_machine.add_product_group("not a group")


def test_add_product_group_no_rates_uses_machine_defaults():
    run_rate = Unit(50)
    per = Mins(1)
    mach = ContinuousMachine(
        "APG Defaults Mach", default_run_rate=run_rate, default_per=per
    )
    prod_a = ContinuousProduct("APG Defaults A", base_dimension=BaseUnit)
    prod_b = ContinuousProduct("APG Defaults B", base_dimension=BaseUnit)
    group = ProductGroup("APG Defaults Group", [prod_a, prod_b])

    mach.add_product_group(group)

    assert set(mach._products.keys()) == {prod_a._id, prod_b._id}
    assert mach._products[prod_a._id]["run_rate"] is run_rate
    assert mach._products[prod_b._id]["run_rate"] is run_rate


def test_add_product_group_no_default_and_no_rates_raises_machine_error(
    cont_machine,
):
    prod = ContinuousProduct("APG No Default", base_dimension=BaseUnit)
    group = ProductGroup("APG No Default Group", [prod])

    with pytest.raises(
        MachineError,
        match="Neither a default nor specific run rate is specified",
    ):
        cont_machine.add_product_group(group)


def test_add_product_group_mismatched_run_rates_length_raises_machine_error(
    cont_machine,
):
    prod = ContinuousProduct("APG Mismatch", base_dimension=BaseUnit)
    group = ProductGroup("APG Mismatch Group", [prod])

    with pytest.raises(
        MachineError, match="either must all be specified or completely"
    ):
        cont_machine.add_product_group(group, run_rates=[])


def test_add_product_group_custom_run_rates_applied_per_product(
    cont_machine,
):
    prod = ContinuousProduct("APG Custom", base_dimension=BaseUnit)
    group = ProductGroup("APG Custom Group", [prod])
    run_rate = Unit(20)
    per = Mins(1)

    cont_machine.add_product_group(
        group,
        run_rates=[
            {"prod_name": "APG Custom", "run_rate": run_rate, "per": per}
        ],
    )

    entry = cont_machine._products[prod._id]
    assert entry["run_rate"] is run_rate
    assert entry["run_rate_per"] is per


def test_add_product_group_custom_run_rates_disambiguate_by_code(
    cont_machine,
):
    prod_uk = ContinuousProduct(
        "APG Code Dup", base_dimension=BaseUnit, code="UK"
    )
    prod_us = ContinuousProduct(
        "APG Code Dup", base_dimension=BaseUnit, code="US"
    )
    group = ProductGroup("APG Code Group", [prod_uk, prod_us])
    uk_rate = Unit(10)
    us_rate = Unit(20)

    cont_machine.add_product_group(
        group,
        run_rates=[
            {
                "prod_name": "APG Code Dup",
                "prod_code": "UK",
                "run_rate": uk_rate,
                "per": Mins(1),
            },
            {
                "prod_name": "APG Code Dup",
                "prod_code": "US",
                "run_rate": us_rate,
                "per": Mins(1),
            },
        ],
    )

    assert cont_machine._products[prod_uk._id]["run_rate"] is uk_rate
    assert cont_machine._products[prod_us._id]["run_rate"] is us_rate


def test_add_product_group_unknown_product_name_raises_value_error(
    cont_machine,
):
    prod = ContinuousProduct("APG Unknown", base_dimension=BaseUnit)
    group = ProductGroup("APG Unknown Group", [prod])

    with pytest.raises(ValueError, match="Product name not recognised"):
        cont_machine.add_product_group(
            group,
            run_rates=[
                {
                    "prod_name": "Does Not Exist",
                    "run_rate": Unit(1),
                    "per": Mins(1),
                }
            ],
        )


# ===========================================================================
# add_hard_constraint (machine-level)
# ===========================================================================


def test_add_hard_constraint_single_sets_machine_and_level(cont_machine):
    con = MinProductionTime(Hours(4))

    cont_machine.add_hard_constraint(con)

    assert cont_machine._hard_constraints == [con]
    assert con.machine is cont_machine
    assert con._level == ConstraintLevel.MACHINE.value


def test_add_hard_constraint_list(cont_machine):
    con_a = MinProductionTime(Hours(4))
    con_b = MinProductionTime(Hours(6))

    cont_machine.add_hard_constraint([con_a, con_b])

    assert cont_machine._hard_constraints == [con_a, con_b]


def test_add_hard_constraint_wrong_type_raises_type_error(cont_machine):
    with pytest.raises(TypeError, match="must all be of type HardConstraint"):
        cont_machine.add_hard_constraint("not a constraint")


def test_add_hard_constraint_does_not_overwrite_existing_machine(
    cont_machine,
):
    other_machine = ContinuousMachine("AHC Other Machine")
    con = MinProductionTime(Hours(4))
    con._set_machine(other_machine)

    cont_machine.add_hard_constraint(con)

    # The machine reference is only set if it wasn't already, but the level
    # is always updated to reflect where `add_hard_constraint` was called.
    assert con.machine is other_machine
    assert con._level == ConstraintLevel.MACHINE.value


# ===========================================================================
# ContinuousMachineGroup
# ===========================================================================


def test_machine_group_init_empty():
    group = ContinuousMachineGroup("TM Group Empty")

    assert group.machines == []


def test_machine_group_init_with_machines():
    mach_a = ContinuousMachine("TM Group Init A")
    mach_b = ContinuousMachine("TM Group Init B")

    group = ContinuousMachineGroup("TM Group Init", [mach_a, mach_b])

    assert set(group.machines) == {mach_a, mach_b}


def test_machine_group_init_wrong_type_raises_type_error():
    with pytest.raises(TypeError, match="Incorrect type added to machine"):
        ContinuousMachineGroup("TM Group Bad Init", ["not a machine"])


def test_machine_group_add_machine_single_and_list():
    group = ContinuousMachineGroup("TM Group Add")
    mach_a = ContinuousMachine("TM Group Add A")
    mach_b = ContinuousMachine("TM Group Add B")
    mach_c = ContinuousMachine("TM Group Add C")

    group.add_machine(mach_a)
    group.add_machine([mach_b, mach_c])

    assert set(group.machines) == {mach_a, mach_b, mach_c}


def test_machine_group_add_machine_duplicate_warns():
    mach = ContinuousMachine("TM Group Dup")
    group = ContinuousMachineGroup("TM Group Dup Grp")
    group.add_machine(mach)

    with pytest.warns(UserWarning, match="Duplicate machines"):
        group.add_machine(mach)

    # The duplicate is deduplicated away.
    assert group.machines == [mach]


def test_machine_group_add_machine_duplicate_silenced_by_option(
    monkeypatch,
):
    import pro_machina

    monkeypatch.setitem(pro_machina.options, "silence_warnings", True)

    mach = ContinuousMachine("TM Group Dup Silenced")
    group = ContinuousMachineGroup("TM Group Dup Silenced Grp")
    group.add_machine(mach)

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        group.add_machine(mach)

    assert caught == []


def test_machine_group_add_machine_wrong_type_raises_type_error():
    group = ContinuousMachineGroup("TM Group Bad Type")

    with pytest.raises(TypeError, match="Incorrect type added to machine"):
        group.add_machine(["not a machine"])


def test_machine_group_add_machine_raw_string_explodes_into_characters():
    # Regression test: add_machine() only checks types *after* extending
    # self.machines, and a bare string is iterable - each character gets
    # appended as its own "machine" first. With enough repeated characters
    # that even triggers the (spurious) "Duplicate machines" warning before
    # the eventual TypeError. Passing a list (as in the test above) avoids
    # this pitfall.
    group = ContinuousMachineGroup("TM Group Raw String")

    with pytest.warns(UserWarning, match="Duplicate machines"):
        with pytest.raises(TypeError, match="Incorrect type added to machine"):
            group.add_machine("not a machine")
