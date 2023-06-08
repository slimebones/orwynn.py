from unittest.mock import patch

from fastapi import FastAPI
from fastapi.middleware.asyncexitstack import AsyncExitStackMiddleware
from starlette.middleware import Middleware
from starlette.middleware.errors import ServerErrorMiddleware
from starlette.middleware.exceptions import ExceptionMiddleware
from starlette.types import ASGIApp

from orwynn.app.apirouter import ApiRouter


class CoreApp(FastAPI):
    def __init__(self, **kwargs) -> None:
        with patch("fastapi.routing.APIRouter", new=ApiRouter):
            super().__init__(**kwargs)

    def build_middleware_stack(self) -> ASGIApp:
        # Duplicate/override from Starlette to add AsyncExitStackMiddleware
        # inside of ExceptionMiddleware, inside of custom user middlewares
        debug = self.debug
        error_handler = None
        exception_handlers = {}

        for key, value in self.exception_handlers.items():
            if key in (500, Exception):
                error_handler = value
            else:
                exception_handlers[key] = value

        middleware = [
            Middleware(
            ServerErrorMiddleware, handler=error_handler, debug=debug
            ),
            Middleware(
                ExceptionMiddleware,
                handlers=exception_handlers,
                debug=debug
            ),
            *self.user_middleware,
            Middleware(AsyncExitStackMiddleware)
        ]

        app = self.router
        for cls, options in reversed(middleware):
            app = cls(app=app, **options)
        return app
