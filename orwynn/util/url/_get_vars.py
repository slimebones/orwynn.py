import re
from itertools import zip_longest

from orwynn.base.error._MalfunctionError import MalfunctionError

from ._Url import Url
from ._UrlVars import UrlVars


def get_vars(
    url: Url,
    *,
    original_route: str
) -> UrlVars:
    """
    Inspects the given url to find all path and query vars.

    Args:
        url:
            Url to inspect.
        original_route:
            Route with formatting blocks for route vars included.

    Returns:
        Dict formed of path and query vars.
    """
    final: UrlVars = UrlVars(
        url=url,
        original_route=original_route,
        path_vars={},
        query_vars={}
    )
    _set_path_vars(final)
    if url.query != "":
        _set_query_vars(final)
    return final


def _set_path_vars(
    vars: UrlVars
) -> None:
    path_var_names: list[str] = re.findall(
        r"\{\w+\}",
        vars.original_route
    )
    path_var_names = [
        name.replace("{", "").replace("}", "") for name in path_var_names
    ]

    regex_ready_original_route: str = re.sub(
        r"\\{\w+\\}",
        r"(\\w+)",
        re.escape(vars.original_route)
    )
    path_match = re.search(
        re.compile(regex_ready_original_route),
        vars.url.path
    )
    if path_match:
        for var_name, var_value in zip_longest(
            path_var_names, path_match.groups()
        ):
            if var_name is None or var_value is None:
                raise MalfunctionError(
                    "unmatched amount of "
                )

            vars.path_vars[var_name] = var_value


def _set_query_vars(
    vars: UrlVars
) -> None:
    query: str = vars.url.query
    query_elements: list[str] = query.split("&")
    for el in query_elements:
        if el == "":
            continue
        name, value = el.split("=")
        vars.query_vars[name] = value
