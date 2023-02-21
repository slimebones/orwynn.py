from orwynn.src.middleware.DispatchWebsocketFn import DispatchWebsocketFn
from orwynn.src.middleware.GenericWebsocketFn import GenericWebsocketFn
from orwynn.src.model.Model import Model


class WebsocketHandler(Model):
    fn: GenericWebsocketFn
    route: str


class DispatchWebsocketHandler(WebsocketHandler):
    fn: DispatchWebsocketFn
    # Middleware is responding to all routes, but inside own dispatch function
    # decides whether to handle it or not.
    route: str = "*"
