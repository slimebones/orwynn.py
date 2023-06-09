from pydantic import BaseModel

from orwynn.utils.url.url import Url


class UrlVars(BaseModel):
    url: Url
    abstract_route: str
    path_vars: dict[str, str]
    query_vars: dict[str, str]

    class Config:
        arbitrary_types_allowed = True
