from orwynn import web
from orwynn.error.Error import Error
from orwynn.middleware.BuiltinHttpMiddleware import BuiltinHttpMiddleware
from orwynn.middleware.HttpNextCallFn import HttpNextCallFn


class ErrorCatchBuiltinMiddleware(BuiltinHttpMiddleware):
    """Catches all errors happened at middleware level.

    Should be outermost defined middleware, even among builtin ones.

    Since in Starlette middlewares handle the response latter than error
    handlers, it's required to define own error handlers in middlewares too.

    To not complicate each middleware process() method with error handling,
    this middleware is introduced.
    """
    async def process(
        self,
        request: web.Request,
        call_next: HttpNextCallFn
    ) -> web.Response:
        # TODO: Move error handling logic from here and error handlers to
        #   the unified method to not repeat things.
        try:
            return await call_next(request)
        except Error as err:
            return web.JSONResponse(err.api, err.status_code)
        except Exception as err:  # noqa: BLE001
            return web.JSONResponse(" ; ".join(err.args), 400)
