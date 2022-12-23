from typing import TYPE_CHECKING
from orwynn.base.worker._Worker import Worker

if TYPE_CHECKING:
    from orwynn import Indication


class APIIndicationOnlyProxy(Worker):
    def __init__(self, api_indication: "Indication") -> None:
        super().__init__()
        self.api_indication = api_indication
