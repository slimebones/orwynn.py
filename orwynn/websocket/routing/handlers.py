from orwynn.model.model import Model

from .dispatchfunc import DispatchWebsocketFn
from .genericfunc import GenericWebsocketFn


class WebsocketHandler(Model):
    func: GenericWebsocketFn
    route: str


class DispatchWebsocketHandler(WebsocketHandler):
    func: DispatchWebsocketFn
    # Middleware is responding to all routes, but inside own dispatch function
    # decides whether to handle it or not.
    route: str = "*"
