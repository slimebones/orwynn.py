from orwynn.di.constants import BUILTIN_PROVIDERS


def is_provider(Class: type) -> bool:
    """Checks if given class is a Provider.

    Args:
        Class:
            Any class to check to.

    Returns:
        Flag signifies if given class is a Provider.
    """
    return issubclass(Class, tuple(BUILTIN_PROVIDERS))
