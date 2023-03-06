def get_exception_direct_subclasses() -> list[type[Exception]]:
    """
    Returns all base Exception direct subclasses.
    """
    all_exceptions: list[type[Exception]] = Exception.__subclasses__()
    return all_exceptions
