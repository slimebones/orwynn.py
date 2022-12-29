from orwynn.app.App import App
from orwynn.controller.endpoint.Endpoint import Endpoint
from orwynn.controller.http.HTTPController import HTTPController
from orwynn.module.Module import Module
from orwynn.service.Service import Service


class FloatService(Service):
    def __init__(self, app: App) -> None:
        super().__init__()
        self._app = app

    def find(self, id: str) -> float:
        number: float = 0

        for x in id:
            number += ord(x) * 0.5

        return number


class FloatController(HTTPController):
    ROUTE = "/"
    ENDPOINTS = [Endpoint(method="get")]

    def __init__(self, service: FloatService) -> None:
        super().__init__()
        self.service = service

    def get(self, id: str) -> dict:
        return {
            "type": "float",
            "value": self.service.find(id)
        }


float_module = Module(
    route="/floats",
    Providers=[FloatService],
    Controllers=[FloatController]
)
