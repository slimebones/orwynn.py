from pathlib import Path

import lorem

from orwynn.app.app_service import AppService
from orwynn.base.config.config import Config
from orwynn.base.controller.controller import Controller
from orwynn.base.module.module import Module
from orwynn.base.service.service import Service
from orwynn.validation import model_validator
from tests.std.float import FloatService, float_module
from tests.std.number import NumberService, number_module


class TextConfig(Config):
    SOURCE = Path("tests/std/text.yml")
    words_amount: int

    @model_validator("words_amount")
    def is_in_allowed_range(cls, v):
        if not 1 <= v <= 20:
            raise ValueError("{} must be in range 1-20".format(v))
        return v


class TextService(Service):
    def __init__(
        self,
        config: TextConfig,
        app: AppService,
        number_service: NumberService,
        float_service: FloatService
    ) -> None:
        super().__init__()
        self.words_amount = config.words_amount
        self._app = app
        self._number_service = number_service
        self._float_service = float_service

    def find(self, id: str) -> str:
        return "{}: {}".format(
            id, " ".join(lorem.text().split()[:self.words_amount])
        )


class TextController(Controller):
    ROUTE = "/"

    def __init__(self, service: TextService) -> None:
        super().__init__()
        self.service = service

    def get(self, id: str) -> dict:
        return {
            "type": "str",
            "value": self.service.find(id)
        }


text_module = Module(
    route="/text",
    Providers=[TextService, TextConfig],
    Controllers=[TextController],
    imports=[number_module, float_module]
)
