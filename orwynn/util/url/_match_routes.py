import re


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
