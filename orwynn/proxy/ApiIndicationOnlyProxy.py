from typing import TYPE_CHECKING

from orwynn.base.worker import Worker

if TYPE_CHECKING:
    from orwynn.indication import Indication


class ApiIndicationOnlyProxy(Worker):
    def __init__(self, api_indication: "Indication") -> None:
        super().__init__()
        self.api_indication = api_indication
