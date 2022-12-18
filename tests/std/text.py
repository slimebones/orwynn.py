from pathlib import Path

import lorem

from orwynn.app.AppService import AppService
from orwynn.base.config.Config import Config
from orwynn.base.controller.Controller import Controller
from orwynn.base.model.Model import Model
from orwynn.base.module.module import Module
from orwynn.base.service.service import Service
from orwynn.boot.BootConfig import BootConfig
from orwynn.util.validation.validation import model_validator
from tests.std.float import FloatService, float_module
from tests.std.number import NumberService, number_module


DEFAULT_ID: str = "e55"


class Text(Model):
    text: str


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
        float_service: FloatService,
        boot_config: BootConfig
    ) -> None:
        super().__init__()
        self.words_amount = config.words_amount
        self._app = app
        self._number_service = number_service
        self._float_service = float_service
        self._mode = boot_config.mode

    def find(self, id: str) -> Text:
        return Text(
            text="{}: {}".format(
                id, " ".join(lorem.text().split()[:self.words_amount])
            )
        )


class TextController(Controller):
    ROUTE = "/"
    METHODS = ["get"]

    def __init__(self, service: TextService) -> None:
        super().__init__()
        self.service = service

    def get(self) -> dict:
        return self.service.find(DEFAULT_ID).api


text_module = Module(
    route="/text",
    Providers=[TextService, TextConfig, BootConfig],
    Controllers=[TextController],
    imports=[number_module, float_module]
)
