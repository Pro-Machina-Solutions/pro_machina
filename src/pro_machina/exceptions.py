class ProblemError(Exception):
    """An exception raised during problem specification"""


class ShiftIntegrityError(ProblemError):
    """The final shift pattern built has an internal error in its definition"""


class ShiftDefinitionError(ProblemError):
    """The user has specified the shift parameters incorrectly"""
