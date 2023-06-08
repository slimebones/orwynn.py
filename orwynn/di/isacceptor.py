from orwynn.di.constants import BUILTIN_ACCEPTORS


def is_acceptor(Class: type) -> bool:
    """Checks if given class is an Acceptor.

    Args:
        Class:
            Any class to check to.

    Returns:
        Flag signifies if given class is an Acceptor.
    """
    return issubclass(Class, tuple(BUILTIN_ACCEPTORS))
