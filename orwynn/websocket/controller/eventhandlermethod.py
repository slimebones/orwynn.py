from typing import Callable

from orwynn.model.model import Model


class WebsocketEventHandlerMethod(Model):
    name: str
    fn: Callable
