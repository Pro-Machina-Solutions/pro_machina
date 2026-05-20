from itertools import count
from warnings import warn

import pro_machina

from ..machines import _Machine


class PairedMachines:
    """Create a pairing of machines that must produce the same product

    In some cases you may have multiple machines that feed into the same
    downstream unit e.g. a single boxer/palletizer. In these instances, when
    the machines are active together then they must be making the same product.
    This does not mean that a pair of machines must share the same shift
    pattern but in the instances when more than one of the paired machines are
    operating, they will produce the same product.

    Parameters
    ----------
    name : str
        A name for the grouping
    machines : list[_Machine] | None, optional
        Optionally instantiate the group with a list of pre-defined
        machines. Otherwise, you can instantitate an empty group and add
        machines to it as and when they are defined in your code

    Raises
    ------
    TypeError
        Attempted to add something other than a Machine to the grouping
    """

    _ids = count(0)

    def __init__(
        self, name: str, machines: list[_Machine] | None = None
    ) -> None:
        self._id = next(self._ids)
        self.name = name
        self.machines: list[_Machine] = (
            machines if machines is not None else []
        )
        if self.machines:
            if not all(isinstance(item, _Machine) for item in self.machines):
                raise TypeError("Incorrect type added to paired machines")

    def add_machines(self, machines: _Machine | list[_Machine]) -> None:
        """Add a machine to an existing grouping

        Parameters
        ----------
        machines : _Machine | list[_Machine]
            The machine(s) to be added

        Raises
        ------
        TypeError
            Attempted to add something other than a Machine to the grouping
        """
        if isinstance(machines, _Machine):
            self.machines.append(machines)
        else:
            self.machines.extend(machines)

        if not all(isinstance(item, _Machine) for item in self.machines):
            raise TypeError("Incorrect type added to paired machines")

        prev_len = len(self.machines)
        self.products = list(set(self.machines))
        if (
            len(self.machines) < prev_len
            and not pro_machina.options["silence_warnings"]
        ):
            warn(
                f"\n Duplicate machines were added to pairing: {self.name}\n",
                stacklevel=3,
            )


class MutuallyExclusiveMachines:
    """Create a grouping of machines that cannot run at the same time

    The simplest use-case for this grouping is having a single machine that can
    run in multiple configurations. That is, by changing the physical setup of
    a single machine, it can make an entirely different subset of products.

    Practically, on the shop floor, it's a single machine but in the Problem we
    would model this as two machines: Machine_1_config_A and Machine_1_config_B
    for example. We then set both of these machines into a single
    MutallyExclusiveMachines grouping such that only one of those variations
    can actually be producing at any one time.

    Parameters
    ----------
    name : str
        A name for the grouping
    machines : list[_Machine] | None, optional
        Optionally instantiate the group with a list of pre-defined
        machines. Otherwise, you can instantitate an empty group and add
        machines to it as and when they are defined in your code

    Raises
    ------
    TypeError
        Attempted to add something other than a Machine to the grouping
    """

    _ids = count(0)

    def __init__(
        self, name: str, machines: list[_Machine] | None = None
    ) -> None:
        self._id = next(self._ids)
        self.name = name
        self.machines: list[_Machine] = (
            machines if machines is not None else []
        )
        if self.machines:
            if not all(isinstance(item, _Machine) for item in self.machines):
                raise TypeError(
                    "Incorrect type added to mutually exclusive machines"
                )

    def add_machines(self, machines: _Machine | list[_Machine]) -> None:
        """Add a machine to an existing grouping

        Parameters
        ----------
        machines : _Machine | list[_Machine]
            The machine(s) to be added

        Raises
        ------
        TypeError
            Attempted to add something other than a Machine to the grouping
        """
        if isinstance(machines, _Machine):
            self.machines.append(machines)
        else:
            self.machines.extend(machines)

        if not all(isinstance(item, _Machine) for item in self.machines):
            raise TypeError(
                "Incorrect type added to mutually exclusive machines"
            )

        prev_len = len(self.machines)
        self.products = list(set(self.machines))
        if (
            len(self.machines) < prev_len
            and not pro_machina.options["silence_warnings"]
        ):
            warn(
                "\n Duplicate machines were added to mutually exclusive"
                f" pairing: {self.name}\n",
                stacklevel=3,
            )
