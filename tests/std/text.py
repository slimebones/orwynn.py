import lorem
from orwynn.base.config.config import Config
from orwynn.base.controller.controller import Controller
from orwynn.base.module.module import Module
from orwynn.base.service.service import Service
from tests.std.number import number_module
from orwynn.util.validation import model_validator


class TextConfig(Config):
    words_amount: int

    @model_validator("words_amount")
    def is_in_allowed_range(cls, v):
        if not 1 <= v <= 20:
            raise ValueError("{} must be in range 1-20".format(v))
        return v


class TextService(Service):
    def __init__(self, config: TextConfig) -> None:
        super().__init__()
        self.words_amount = config.words_amount

    def find(self, id: str) -> str:
        return "{}: {}".format(
            id, " ".join(lorem.text().split()[:self.words_amount])
        )


class TextController(Controller):
    ROUTE = "/"

    def __init__(self, service: TextService) -> None:
        super().__init__()
        self.service = service

    def find(self, id: str) -> dict:
        return {
            "type": "str",
            "value": self.service.find(id)
        }


text_module = Module(
    route="/text",
    Providers=[TextService, TextConfig],
    Controllers=[TextController],
    imports=[number_module]
)
