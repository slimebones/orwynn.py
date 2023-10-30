from orwynn.app import App
from orwynn.base.module import Module
from orwynn.base.service import Service
from orwynn.http import Endpoint, HttpController


class FloatService(Service):
    def __init__(self, app: App) -> None:
        super().__init__()
        self._app = app

    def find(self, id: str) -> float:
        number: float = 0

        for x in id:
            number += ord(x) * 0.5

        return number


class FloatController(HttpController):
    Route = "/"
    Endpoints = [Endpoint(method="get")]

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
    Controllers=[FloatController],
    exports=[FloatService]
)
