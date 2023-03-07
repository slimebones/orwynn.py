from orwynn.base.model import Model
from orwynn.http import Endpoint, HttpController

GET_DATA: dict = {"message": "hello"}


class GetHttpController(HttpController):
    ROUTE = "/"
    ENDPOINTS = [
        Endpoint(method="get")
    ]

    def get(self) -> dict:
        return GET_DATA


class IdGetHttpController(HttpController):
    ROUTE = "/{id}"
    ENDPOINTS = [
        Endpoint(method="get")
    ]

    def get(self, id: str) -> dict:
        return {"id": id}


class Item(Model):
    name: str
    price: float
    order: int = 0
