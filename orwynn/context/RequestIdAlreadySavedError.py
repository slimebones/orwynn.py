from orwynn.base.error.Error import Error


class RequestIdAlreadySavedError(Error):
    """If the request id is attempted to be saved twice."""
