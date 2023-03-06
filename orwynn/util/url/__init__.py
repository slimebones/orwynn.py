"""
Works with url formatting.
"""
from orwynn.util import validation

from ._get_vars import get_vars
from orwynn.util.url._match_routes import match_routes
from ._Url import Url
from ._UrlVars import UrlVars


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


