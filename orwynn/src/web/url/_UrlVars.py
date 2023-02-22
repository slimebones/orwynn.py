from orwynn.src.model.Model import Model

from ._Url import Url


class UrlVars(Model):
    url: Url
    original_route: str
    path_vars: dict[str, str]
    query_vars: dict[str, str]

    class Config:
        arbitrary_types_allowed = True
