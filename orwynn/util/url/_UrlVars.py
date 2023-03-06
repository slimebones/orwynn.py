from orwynn.base.model._Model import Model

from ._Url import Url


class UrlVars(Model):
    url: Url
    abstract_route: str
    path_vars: dict[str, str]
    query_vars: dict[str, str]

    class Config:
        arbitrary_types_allowed = True
