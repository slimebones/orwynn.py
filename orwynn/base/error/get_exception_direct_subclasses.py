from orwynn.base.error.Error import Error


def get_exception_direct_subclasses() -> list[type[Exception]]:
    """
    Returns all base Exception direct subclasses but not Orwynn.Error.
    """
    all_exceptions: list[type[Exception]] = Exception.__subclasses__()
    all_exceptions.remove(Error)
    return all_exceptions
