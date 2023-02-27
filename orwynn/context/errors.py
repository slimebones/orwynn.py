from orwynn.base.error import Error


class AlreadyInitializedStorageError(Error):
    """If the context storage has been already initialized."""


class RequestIdAlreadySavedError(Error):
    """If the request id is attempted to be saved twice."""


class UndefinedStorageError(Error):
    """Storage is not set for the current context."""
