from orwynn.app.app import App
from orwynn.base.module.module import Module
from orwynn.base.service.service import Service
from orwynn.http import Endpoint, HttpController
from tests.std.float import FloatService, float_module


class NumberService(Service):
    def __init__(self, app: App, float_service: FloatService) -> None:
        super().__init__()
        self._app = app
        self._float_service = float_service

    def find(self, id: str) -> int:
        number: int = 0

        for x in id:
            number += ord(x)

        return number


class NumberController(HttpController):
    Route = "/"
    Endpoints = [Endpoint(method="get")]

    def __init__(self, service: NumberService) -> None:
        super().__init__()
        self.service = service

    def get(self, id: str) -> dict:
        return {
            "type": "int",
            "value": self.service.find(id)
        }


number_module = Module(
    route="/numbers",
    Providers=[NumberService],
    Controllers=[NumberController],
    imports=[float_module],
    exports=[NumberService]
)
