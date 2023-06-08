from typing import Callable

from orwynn.base.model.model import Model


class WebsocketEventHandlerMethod(Model):
    name: str
    fn: Callable
