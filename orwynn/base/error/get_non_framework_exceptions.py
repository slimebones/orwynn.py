from orwynn.base.error.Error import Error


def get_non_framework_exceptions() -> list[type[Exception]]:
    all_exceptions: list[type[Exception]] = Exception.__subclasses__()
    all_exceptions.remove(Error)
    return all_exceptions
