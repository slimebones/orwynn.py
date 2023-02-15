from orwynn import web
from orwynn.log.HttpLogger import HttpLogger
from orwynn.middleware.HttpMiddleware import HttpMiddleware
from orwynn.middleware.HttpNextCallFn import HttpNextCallFn
from orwynn.web.context.RequestContextId import RequestContextId


class LogMiddleware(HttpMiddleware):
    """Logs information about request and response lihking them together.

    It's recommended to be outermost (at custom level) middleware.
    """
    def __init__(self, covered_routes: list[str]) -> None:
        super().__init__(covered_routes)

        self.__http_logger: HttpLogger = HttpLogger()

    async def process(
        self, request: web.Request, call_next: HttpNextCallFn
    ) -> web.Response:
        request_id: str = RequestContextId().get()
        await self.__http_logger.log_request(
            request,
            request_id
        )

        response: web.Response = await call_next(request)

        await self.__http_logger.log_response(
            response,
            request=request,
            request_id=request_id
        )

        return response
