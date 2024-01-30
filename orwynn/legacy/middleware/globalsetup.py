from .middleware import Middleware

GlobalMiddlewareSetup = dict[type[Middleware], list[str]]
