from orwynn.error.Error import Error


class NothingToValidateError(Error):
    """Typically raised if an empty structure is passed to validation function.
    """
    pass
