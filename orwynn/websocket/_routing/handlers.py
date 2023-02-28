from orwynn.base.model._Model import Model

from ._DispatchWebsocketFn import DispatchWebsocketFn
from ._GenericWebsocketFn import GenericWebsocketFn


class WebsocketHandler(Model):
    fn: GenericWebsocketFn
    route: str


class DispatchWebsocketHandler(WebsocketHandler):
    fn: DispatchWebsocketFn
    # Middleware is responding to all routes, but inside own dispatch function
    # decides whether to handle it or not.
    route: str = "*"
