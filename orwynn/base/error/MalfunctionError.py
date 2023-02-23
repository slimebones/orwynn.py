from orwynn.base.error.Error import Error


class MalfunctionError(Error):
    """Something wrong with the system workflow.

    Rare error signifies problems with framework's source code.
    """
