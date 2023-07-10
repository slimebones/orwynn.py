"""
Works with url formatting.
"""
from orwynn.utils import validation
from orwynn.utils.url.utils import match_routes

from .helpers import get_vars
from .url import Url
from .vars import UrlVars


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
