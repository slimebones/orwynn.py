class MalfunctionError(Exception):
    """Something wrong with the system workflow.

    Rare error signifies problems with framework's source code.
    """


class ExceptionAlreadyHandledError(Exception):
    """
    The exception class is handled more by one error handler.
    """
