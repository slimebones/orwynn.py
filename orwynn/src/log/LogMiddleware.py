from orwynn.src.log.HttpLogger import HttpLogger
from orwynn.src.middleware.HttpMiddleware import HttpMiddleware
from orwynn.src.middleware.HttpNextCall import HttpNextCall
from orwynn.src.web.context.RequestContextId import RequestContextId
from orwynn.src.web.http.requests import HttpRequest
from orwynn.src.web.http.responses import HttpResponse


class LogMiddleware(HttpMiddleware):
    """Logs information about request and response lihking them together.

    It's recommended to be outermost (at custom level) middleware.
    """
    def __init__(self, covered_routes: list[str]) -> None:
        super().__init__(covered_routes)

        self.__http_logger: HttpLogger = HttpLogger()

    async def process(
        self, request: HttpRequest, call_next: HttpNextCall
    ) -> HttpResponse:
        request_id: str = RequestContextId().get()
        await self.__http_logger.log_request(
            request,
            request_id
        )

        response: HttpResponse = await call_next(request)

        await self.__http_logger.log_response(
            response,
            request=request,
            request_id=request_id
        )

        return response
