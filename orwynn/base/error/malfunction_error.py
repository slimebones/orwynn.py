from orwynn.base.error.error import Error


class MalfunctionError(Error):
    """Something wrong with the object workflow.

    Rare error signifies problems with framework's source code.
    """
    pass
