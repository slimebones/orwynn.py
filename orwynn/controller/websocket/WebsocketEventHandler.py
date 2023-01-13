from typing import Callable
from orwynn.model.Model import Model


class WebsocketEventHandler(Model):
    name: str
    fn: Callable
