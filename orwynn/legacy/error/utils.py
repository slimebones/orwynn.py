def find_detailed_class_for_exception(
    exception: Exception,
    Exceptions: list[type[Exception]]
) -> type[Exception]:
    """
    Searches for the most detailed exception class for which occured exception
    is an instance.

    Args:
        exception:
            Exception to search for.
        Exceptions:
            List of exceptions to search within. It can be previously sorted
            by detail level to optimize if it is possible.

    Returns:
        Parent Exception class with the most detailed level.
    """
    # Get the most detailed (last in the sorted list) class which is also a
    # parent of the given instance.
    return __sort_by_detail([
        Exc for Exc in Exceptions if isinstance(exception, Exc)
    ])[-1]


def __sort_by_detail(
    Exceptions: list[type[Exception]]
) -> list[type[Exception]]:
    """
    Returns a new sorted by detail (lower index -> lower detail) list of
    exceptions.
    """
    copied: list[type[Exception]] = Exceptions.copy()

    length: int = len(Exceptions)
    is_swapped: bool = False
    for i in range(length):
        for j in range(0, length - i - 1):
            if __is_more_detailed(copied[j], copied[j+1]):
                is_swapped = True
                copied[j], copied[j+1] = copied[j+1], copied[j]
        # Exit the main loop after 0 swaps
        if not is_swapped:
            break

    return copied


def __is_more_detailed(
    Exception1: type[Exception],
    Exception2: type[Exception]
) -> bool:
    """
    Returns True if an Exception1 has more detail level than Exception2 and
    False otherwise. Also returns False if both given exception classes have
    the same level of detail.
    """
    mro1: list[type] = Exception1.mro()

    return (Exception2 in mro1)


def get_exception_direct_subclasses() -> list[type[Exception]]:
    """
    Returns all base Exception direct subclasses.
    """
    all_exceptions: list[type[Exception]] = Exception.__subclasses__()
    return all_exceptions
