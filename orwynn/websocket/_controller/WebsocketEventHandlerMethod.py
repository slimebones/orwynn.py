from typing import Callable

from orwynn.base.model._Model import Model


class WebsocketEventHandlerMethod(Model):
    name: str
    fn: Callable
