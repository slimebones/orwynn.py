from orwynn.app.AppService import AppService
from orwynn.base.controller._Controller import Controller
from orwynn.base.module.Module import Module
from orwynn.base.service.Service import Service


class FloatService(Service):
    def __init__(self, app: AppService) -> None:
        super().__init__()
        self._app = app

    def find(self, id: str) -> float:
        number: float = 0

        for x in id:
            number += ord(x) * 0.5

        return number


class FloatController(Controller):
    ROUTE = "/"
    METHODS = ["get"]

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
