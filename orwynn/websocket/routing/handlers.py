from orwynn.base.model.model import Model

from .dispatchfn import DispatchWebsocketFn
from .genericfn import GenericWebsocketFn


class WebsocketHandler(Model):
    fn: GenericWebsocketFn
    route: str


class DispatchWebsocketHandler(WebsocketHandler):
    fn: DispatchWebsocketFn
    # Middleware is responding to all routes, but inside own dispatch function
    # decides whether to handle it or not.
    route: str = "*"
