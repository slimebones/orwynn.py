from pprint import pprint
from orwynn.base.controller.Controller import Controller
from orwynn.base.controller.endpoint import Endpoint
from orwynn.base.model.Model import Model
from orwynn.base.module.Module import Module
from orwynn.base.test.HttpClient import HttpClient
from orwynn.boot.Boot import Boot


def test_tmp():
    class Item(Model):
        name: str
        price: float

    class C1(Controller):
        ROUTE = "/"
        ENDPOINTS = [Endpoint(method="get")]

        def get(self) -> dict:
            return {"hello": 1}

    boot: Boot = Boot(
        Module(route="/", Controllers=[C1])
    )
    http: HttpClient = boot.app.http_client

    assert False
