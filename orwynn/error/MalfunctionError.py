from orwynn.error.Error import Error


class MalfunctionError(Error):
    """Something wrong with the object workflow.

    Rare error signifies problems with framework's source code.
    """
    pass
