import re
from itertools import zip_longest

from orwynn.utils.url.url import Url
from orwynn.utils.url.utils import match_routes
from orwynn.utils.url.vars import UrlVars


def get_vars(
    url: Url,
    *,
    abstract_route: str
) -> UrlVars:
    """
    Inspects the given url to find all path and query vars.

    Args:
        url:
            Url to inspect.
        abstract_route:
            Route with formatting blocks for route vars included.

    Returns:
        Dict formed of path and query vars.
    """
    final: UrlVars = UrlVars(
        url=url,
        abstract_route=abstract_route,
        path_vars={},
        query_vars={}
    )
    _set_path_vars(final)
    if url.query != "":
        _set_query_vars(final)
    return final


def _set_path_vars(
    url_vars: UrlVars
) -> None:
    path_var_names: list[str] = re.findall(
        r"\{\w+\}",
        url_vars.abstract_route
    )

    # Remove brackets from each element in acquired path variable names
    path_var_names = [
        name.replace("{", "").replace("}", "") for name in path_var_names
    ]

    path_match = match_routes(
        abstract_route=url_vars.abstract_route,
        real_route=url_vars.url.path
    )

    if path_match:
        for var_name, var_value in zip_longest(
            path_var_names, path_match.groups()
        ):
            if var_name is None or var_value is None:
                raise ValueError(
                    "unmatched amount of variable names and it's values in"
                    " given abstract and real routes"
                )

            url_vars.path_vars[var_name] = var_value


def _set_query_vars(
    url_vars: UrlVars
) -> None:
    query: str = url_vars.url.query
    query_elements: list[str] = query.split("&")
    for el in query_elements:
        if el == "":
            continue
        name, value = el.split("=")
        url_vars.query_vars[name] = value
