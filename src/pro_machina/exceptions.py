class ProblemError(Exception):
    """An exception raised during problem specification"""


class ShiftError(ProblemError):
    """Some aspect of the shift pattern definition is invalid"""
