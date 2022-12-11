from orwynn.base.controller.controller import Controller
from orwynn.base.module.module import Module
from orwynn.base.service.service import Service


class NumberService(Service):
    def __init__(self) -> None:
        super().__init__()

    def find(self, id: str) -> int:
        number: int = 0

        for x in id:
            number += ord(x)

        return number


class NumberController(Controller):
    ROUTE = "/"

    def __init__(self, service: NumberService) -> None:
        super().__init__()
        self.service = service

    def find(self, id: str) -> dict:
        return {
            "type": int,
            "value": self.service.find(id)
        }


number_module = Module(
    route="/numbers",
    Providers=[NumberService],
    Controllers=[NumberController]
)
