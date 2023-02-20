from orwynn.middleware.Middleware import Middleware

GlobalMiddlewareSetup = dict[type[Middleware], list[str]]
