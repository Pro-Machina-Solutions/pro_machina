from __future__ import annotations

from itertools import count
from typing import TYPE_CHECKING, NewType

from .measures import Quantity, SizedDimension

if TYPE_CHECKING:
    from .problem.machines import MachID, MachineSubtype
    from .problem.products import (
        ProdGroupID,
        ProdID,
        ProdSubtype,
        ProductGroup,
    )

LocID = NewType("LocID", int)
StorageID = NewType("StorageID", int)
FactoryID = NewType("FactoryID", int)
DeptID = NewType("DeptID", int)

FactoryName = NewType("FactoryName", str)
DeptName = NewType("DeptName", str)


class _Location:
    _ids = count(0)

    def __init__(self):
        self._loc_id = LocID(next(self._ids))


class Factory(_Location):
    _ids = count(0)

    def __init__(
        self, name: str, departments: Department | list[Department] | None
    ):
        super().__init__()
        self._id = FactoryID(next(self._ids))
        self.name = FactoryName(name)

        self._depts_by_id: dict[DeptID, Department] = {}
        self._depts_by_name: dict[DeptName, Department] = {}

        if departments is not None:
            self.add_departments(departments)

    def add_departments(self, departments: Department | list[Department]):

        if isinstance(departments, Department):
            departments = [departments]

        if not all(isinstance(dept, Department) for dept in departments):
            raise TypeError("Invalid Department type.")

        for dept in departments:
            dept._factory = self
            self._depts_by_id[dept._id] = dept
            self._depts_by_name[dept.name] = dept


class Department(_Location):
    _ids = count(0)

    def __init__(
        self,
        name: str,
        machines: MachineSubtype | list[MachineSubtype] | None = None,
    ):
        super().__init__()
        self._id = DeptID(next(self._ids))
        self.name = DeptName(name)
        self._factory: Factory | None = None

        self._machs_by_id: dict[MachID, MachineSubtype] = {}
        self._machs_by_name: dict[str, MachineSubtype] = {}

        if isinstance(machines, MachineSubtype):
            machines = [machines]

        if machines is not None:
            for mach in machines:
                self.add_machines(mach)

    def add_machines(self, machines: MachineSubtype | list[MachineSubtype]):

        if isinstance(machines, MachineSubtype):
            machines = [machines]

        for mach in machines:
            if not isinstance(mach, MachineSubtype):
                raise TypeError("Invalid Machine type.")
            self._machs_by_id[mach._id] = mach
            self._machs_by_name[mach.name] = mach


class Warehouse(_Location):
    _ids = count(0)

    def __init__(self, name: str):
        super().__init__()
        self._id = StorageID(next(self._ids))


class UnsizedStorage(_Location):
    _ids = count(0)

    def __init__(self, name: str):
        super().__init__()
        self._id = StorageID(next(self._ids))


class SizedStorage(_Location):
    _ids = count(0)

    def __init__(
        self,
        name: str,
        total_capacity: Quantity,
        department: Department | None = None,
        factory: Factory | None = None,
    ):
        super().__init__()
        self._id = StorageID(next(self._ids))
        self.name = name
        self.department = department
        self.factory = factory

        self.total_capacity = total_capacity
        self.single_product_limits: dict[
            ProdID, Quantity
        ] = {}
        self.grouped_product_limits: dict[
            ProdGroupID, Quantity
        ] = {}

    def add_single_product_limit(
        self, product: ProdSubtype, limit: Quantity
    ):
        self.single_product_limits[product._id] = limit.resolve(product)

    def add_product_group_limit(
        self, group: ProductGroup, limit: Quantity
    ):
        # Validate now (raises if Pallet isn't sized for a member), but keep
        # the unresolved quantity: it means a different amount per product.
        for prod in group._products.values():
            limit.resolve(prod)
        self.grouped_product_limits[group._id] = limit

    def _check_capacity(self):
        # TODO need to see whether the combined rules for different products
        # overruns the total capacity of the storage unit. Need to think how
        # best to do this
        pass


class LocationMove:
    def __init__(self):
        pass
