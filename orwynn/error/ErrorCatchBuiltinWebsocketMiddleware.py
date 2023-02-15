from orwynn import web
from orwynn.error.Error import Error
from orwynn.middleware.BuiltinWebsocketMiddleware import (
    BuiltinWebsocketMiddleware,
)
from orwynn.middleware.WebsocketNextCallFn import WebsocketNextCallFn


class ErrorCatchBuiltinWebsocketMiddleware(BuiltinWebsocketMiddleware):
    """Catches all errors happened at middleware level.

    Should be outermost defined middleware, even among builtin ones.

    Since in Starlette middlewares handle the response latter than error
    handlers, it's required to define own error handlers in middlewares too.

    To not complicate each middleware process() method with error handling,
    this middleware is introduced.
    """
    async def process(
        self,
        request: web.Websocket,
        call_next: WebsocketNextCallFn
    ) -> None:
        # TODO: Move error handling logic from here and error handlers to
        #   the unified method to not repeat things.
        try:
            return await call_next(request)
        except Error as err:
            return await request.send_json(
                err.api
            )
        except Exception as err:  # noqa: BLE001
            return await request.send_json({
                "type": "error",
                "value": {
                    "message": " ; ".join(err.args)
                }
            })
