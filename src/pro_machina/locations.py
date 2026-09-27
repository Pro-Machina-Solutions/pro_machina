from __future__ import annotations

from itertools import count
from typing import TYPE_CHECKING, NewType

if TYPE_CHECKING:
    from .problem.machines import MachID, MachineSubtype

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
        self._depts_by_name: dict[
            tuple[DeptName, FactoryName], Department
        ] = {}

        if departments is not None:
            self.add_departments(departments)

    def add_departments(self, departments: Department | list[Department]):

        if isinstance(departments, Department):
            departments = [departments]

        if not isinstance(departments, Department):
            raise TypeError("Invalid Department type.")

        for dept in departments:
            dept._factory = self
            self._depts_by_id[departments._id] = dept
            self._depts_by_name[(dept.name, self.name)] = dept


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
        self._department = None

        self._machs_by_id: dict[MachID, MachineSubtype] = {}
        self._machs_by_name: dict[tuple[str, FactoryName], MachineSubtype] = {}

        if isinstance(machines, MachineSubtype):
            machines = [machines]

        if machines is not None:
            for mach in machines:
                self.add_machines(mach)

    def add_machines(self, machines: MachineSubtype | list[MachineSubtype]):

        if isinstance(machines, MachineSubtype):
            machines = [machines]

        if not isinstance(machines, MachineSubtype):
            raise TypeError("Invalid Machine type.")

        for mach in machines:
            self._department = self
            self._factory = self._factory
            self._machs_by_id[mach._id] = mach
            self._machs_by_name[(mach.name, self.name)] = mach


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

    def __init__(self, name: str):
        super().__init__()
        self._id = StorageID(next(self._ids))


class LocationMove:
    def __init__(self):
        pass
