from orwynn.di.BUILTIN_PROVIDERS import BUILTIN_PROVIDERS


def is_provider(Class: type) -> bool:
    """Checks if given class is a Provider.
    
    Args:
        Class:
            Any class to check to.
    
    Returns:
        Flag signifies if given class is a Provider.
    """
    for BuiltinProvider in BUILTIN_PROVIDERS:
        if issubclass(Class, BuiltinProvider):
            return True
    return False