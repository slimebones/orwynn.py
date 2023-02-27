from orwynn.base.error import Error


class DigestingError(Error):
    pass


class UnsupportedIndicatorError(Error):
    pass


class RecoveringError(Error):
    """Wasn't able to recover an object from dictionary using indication."""
