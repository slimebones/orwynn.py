


class AlreadyInitializedStorageError(Exception):
    """If the context storage has been already initialized."""


class RequestIdAlreadySavedError(Exception):
    """If the request id is attempted to be saved twice."""


class UndefinedStorageError(Exception):
    """Storage is not set for the current context."""
