class ProblemError(Exception):
    """An exception raised during problem specification"""


class ShiftIntegrityError(ProblemError):
    """The final shift pattern built has an internal error in its definition"""


class ShiftDefinitionError(ProblemError):
    """The user has specified the shift parameters incorrectly"""


class UnitError(ProblemError):
    """Inconsistency in unit measure types"""


class MachineError(ProblemError):
    """Incorrectly specified parameter for a machine"""


class ConstraintError(ProblemError):
    """Incorrect specification of a constraint"""
