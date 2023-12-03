"""
Works with url formatting.
"""
import re
from enum import Enum
from itertools import zip_longest

from pykit import validation
from pykit.cls import Static
from starlette.datastructures import URL as _StarletteURL

from orwynn.base.model.model import Model

URL = _StarletteURL


class URLScheme(Enum):
    """
    Supported URI schemes.
    """
    HTTP = "http"
    HTTPS = "https"
    Websocket = "websocket"
    RTSP = "rtsp"


class URLVars(Model):
    url: URL
    abstract_route: str
    path_vars: dict[str, str]
    query_vars: dict[str, str]

    class Config:
        arbitrary_types_allowed = True


class URLUtils(Static):
    @staticmethod
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

    @staticmethod
    def get_vars(
        url: URL,
        *,
        abstract_route: str
    ) -> URLVars:
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
        final: URLVars = URLVars(
            url=url,
            abstract_route=abstract_route,
            path_vars={},
            query_vars={}
        )
        URLUtils._set_path_vars(final)
        if url.query != "":
            URLUtils._set_query_vars(final)
        return final

    @staticmethod
    def _set_path_vars(
        url_vars: URLVars
    ) -> None:
        path_var_names: list[str] = re.findall(
            r"\{\w+\}",
            url_vars.abstract_route
        )

        # Remove brackets from each element in acquired path variable names
        path_var_names = [
            name.replace("{", "").replace("}", "") for name in path_var_names
        ]

        path_match = URLUtils.match_routes(
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

    @staticmethod
    def match_routes(
        *,
        abstract_route: str,
        real_route: str
    ) -> re.Match | None:
        """
        Returns match object of comparing real route against an abstract one.
        """
        regex_ready_abstract_route: str = re.sub(
            r"\\{\w+\\}",
            r"(\\w+)",
            re.escape(abstract_route)
        )
        return re.fullmatch(
            re.compile(regex_ready_abstract_route),
            real_route
        )

    @staticmethod
    def _set_query_vars(
        url_vars: URLVars
    ) -> None:
        query: str = url_vars.url.query
        query_elements: list[str] = query.split("&")
        for el in query_elements:
            if el == "":
                continue
            name, value = el.split("=")
            url_vars.query_vars[name] = value


class URLMethod(Enum):
    """
    All possible request methods.
    """
    Get = "get"
    Post = "post"
    Put = "put"
    Delete = "delete"
    Patch = "patch"
    Options = "options"
    Websocket = "websocket"
