
from orwynn import web
from orwynn.error.Error import Error
from orwynn.log.HTTPLogger import HTTPLogger
from orwynn.middleware.Middleware import Middleware, NextCallFn


class LogMiddleware(Middleware):
    """Logs information about request and response lihking them together.

    It's recommended to be outermost (at custom level) middleware.
    """
    def __init__(self, covered_routes: list[str]) -> None:
        super().__init__(covered_routes)

        self.__http_logger: HTTPLogger = HTTPLogger()

    async def process(
        self, request: web.Request, call_next: NextCallFn
    ) -> web.Response:
        # Log the request
        try:
            request_uuid: str = await self.__http_logger.log_request(request)
        except Error as err:
            return web.JSONResponse(err.api, err.status_code)
        except Exception as err:  # noqa: BLE001
            return web.JSONResponse(" ; ".join(err.args), 400)

        response: web.Response = await call_next(request)

        # Log the response
        try:
            await self.__http_logger.log_response(
                response,
                request=request,
                request_uuid=request_uuid
            )
        except Error as err:
            return web.JSONResponse(err.api, err.status_code)
        except Exception as err:  # noqa: BLE001
            return web.JSONResponse(" ; ".join(err.args), 400)

        return response
