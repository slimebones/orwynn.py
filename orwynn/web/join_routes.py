from orwynn import validation


def join_routes(*routes: str) -> str:
    """Joins all given routes and normalize final result."""
    validation.validate_each(routes, str, expected_sequence_type=tuple)

    result: str = ""

    for route in routes:
        if route == "" or route == "/":
            continue
        elif route[0] != "/":
            result += "/" + route
        else:
            result += route
        result.removesuffix("/")

    if result == "":
        result = "/"

    return result
