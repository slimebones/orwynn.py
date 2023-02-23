from .Middleware import Middleware

GlobalMiddlewareSetup = dict[type[Middleware], list[str]]
