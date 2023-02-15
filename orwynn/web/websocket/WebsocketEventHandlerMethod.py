from typing import Callable

from orwynn.model.Model import Model


class WebsocketEventHandlerMethod(Model):
    name: str
    fn: Callable
