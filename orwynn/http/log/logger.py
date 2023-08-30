import contextlib
import json

from starlette.concurrency import iterate_in_threadpool
from starlette.responses import StreamingResponse

from orwynn.base.error import MalfunctionError
from orwynn.http.requests import HttpRequest
from orwynn.http.responses import HttpResponse
from orwynn.log import Log
from orwynn.utils import validation


class HttpLogger:
    """Logs HTTP requests and responses."""
    async def log_request(
        self,
        request: HttpRequest,
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
        validation.validate(request, HttpRequest)
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
            "http": {
                "request": {
                    "id": request_id,
                    # Get full URL
                    "url": request.url._url,
                    "headers": dict(request.headers),
                    "json": json_
                }
            }
        }

        # Note that here and on response field "request_id" also duplicated
        # at extra.request_id by logger itself. It's ok and shouldn't be
        # removed for all logs compliance.
        Log.bind(**extra).info(
            plain_message
        )

        return request_id

    async def log_response(
        self,
        response: HttpResponse,
        *,
        request: HttpRequest,
        request_id: str
    ) -> None:
        """Logs a response linking it to the according request.
        """
        # Fetch response body: for StreamingResponse it should apply special
        # logic.
        response_body: str
        if isinstance(response, StreamingResponse):
            try:
                response_body: str = await self.__get_response_body(response)
            except (UnicodeDecodeError, IndexError):
                response_body = ""
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

        content_type: str = response.headers.get("content-type", "")
        if "application/json" in content_type:
            json_ = validation.apply(
                json.loads(
                    response_body
                ),
                dict
            )
            if not json_:
                json_ = None
        else:
            json_ = None

        extra: dict = {
            "http": {
                "response": {
                    "status_code": response.status_code,
                    "request_id": request_id,
                    "media_type": response.media_type,
                    "headers": dict(response.headers),
                    "json": json_
                }
            }
        }

        Log.bind(**extra).info(
            plain_message
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
