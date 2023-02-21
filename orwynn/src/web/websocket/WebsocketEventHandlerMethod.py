from typing import Callable

from orwynn.src.model.Model import Model


class WebsocketEventHandlerMethod(Model):
    name: str
    fn: Callable
