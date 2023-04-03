import lorem

from orwynn.app._App import App
from orwynn.base.config import Config
from orwynn.base.model._Model import Model
from orwynn.base.module._Module import Module
from orwynn.base.service._Service import Service
from orwynn.boot._BootConfig import BootConfig
from orwynn.http import Endpoint, HttpController
from orwynn.utils.validation import model_validator
from tests.std.float import FloatService, float_module
from tests.std.number import NumberService, number_module
from tests.std.user import user_module

DEFAULT_ID: str = "e55"


class Text(Model):
    text: str


class TextConfig(Config):
    words_amount: int = 2

    @model_validator("words_amount")
    def validate_words_in_range(cls, v):
        if not 1 <= v <= 20:
            raise ValueError(f"{v} must be in range 1-20")
        return v


class TextService(Service):
    def __init__(
        self,
        config: TextConfig,
        app: App,
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


class TextController(HttpController):
    ROUTE = "/"
    ENDPOINTS = [Endpoint(method="get")]

    def __init__(self, service: TextService) -> None:
        super().__init__()
        self.service = service

    def get(self) -> dict:
        return self.service.find(DEFAULT_ID).api


text_module = Module(
    route="/text",
    Providers=[TextService, TextConfig, BootConfig],
    Controllers=[TextController],
    imports=[number_module, float_module, user_module]
)
