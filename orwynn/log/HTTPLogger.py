import contextlib
import json

from starlette.concurrency import iterate_in_threadpool
from starlette.responses import StreamingResponse

from orwynn import validation, web
from orwynn.error.MalfunctionError import MalfunctionError
from orwynn.log.Log import Log


class HTTPLogger:
    """Logs HTTP requests and responses."""
    def __init__(self, log: Log) -> None:
        self.__log = log

    async def log_request(
        self,
        request: web.Request,
        request_id: str
    ) -> str:
        """Assigns special id to request and logs it.

        Args:
            request:
                Request to be logged.
            request_id:
                ID of the request.

        Returns:
            Request assigned ID.
        """
        validation.validate(request, web.Request)
        validation.validate(request_id, str)

        plain_message: str = \
            f"request {request.method.upper()} {request.url.path}" \
            f"{request.url.query}"

        json_: dict | None = None
        with contextlib.suppress(json.JSONDecodeError):
            # FIXME: hangs here, using request.body hangs too, see:
            #   https://github.com/encode/starlette/issues/847
            #
            # Seems like for now no request json will be collected until
            # mentioned issue is resolved.
            json_ = None
        if not json_:
            json_ = None

        extra: dict = {
            "request": {
                "id": request_id,
                # Get full URL
                "url": request.url._url,
                "headers": dict(request.headers),
                "json": json_
            }
        }

        # Note that here and on response field "request_id" also duplicated
        # at extra.request_id by logger itself. It's ok and shouldn't be
        # removed for all logs compliance.
        self.__log.info(
            plain_message, extra=extra
        )

        return request_id

    async def log_response(
        self,
        response: web.Response,
        *,
        request: web.Request,
        request_id: str
    ) -> None:
        """Logs a response linking it to the according request.
        """
        # Fetch response body: for StreamingResponse it should apply special
        # logic.
        response_body: str
        if isinstance(response, StreamingResponse):
            response_body: str = await self.__get_response_body(response)
        else:
            # Interestingly, even returned explicitly JSONResponse handled here
            # as StreamingResponse, so maybe there is not need to handle
            # "else:" branch here.
            raise MalfunctionError(
                f"unexpected branch entering for response {response}"
            )
            # And this is an alternative handling, consider enabling it if you
            # get the MalfunctionError:

        plain_message: str = \
            f"response {response.status_code}" \
            f" {request.url.path}{request.url.query}:" \
            f" {response_body}"
        json_: dict | None
        json_ = validation.apply(
            json.loads(
                response_body
            ),
            dict
        )
        if not json_:
            json_ = None

        extra: dict = {
            "response": {
                "status_code": response.status_code,
                "request_id": request_id,
                "media_type": response.media_type,
                "headers": dict(response.headers),
                "json": json_
            }
        }

        self.__log.info(
            plain_message, extra=extra
        )

    async def __get_response_body(
        self,
        response: StreamingResponse
    ) -> str:
        # Gets response body from StreamingResponse, see:
        #   https://github.com/encode/starlette/issues/874#issuecomment-1027743996
        #
        validation.validate(response, StreamingResponse)

        response_body = [section async for section in response.body_iterator]
        response.body_iterator = iterate_in_threadpool(iter(response_body))
        index0_response_body: bytes = validation.apply(response_body[0], bytes)
        return index0_response_body.decode()
