import contextlib
import json
from typing import Optional
from orwynn import rnd, web, validation
from starlette.concurrency import iterate_in_threadpool
from starlette.responses import StreamingResponse
from orwynn.error.MalfunctionError import MalfunctionError
from orwynn.log.Log import Log


class HTTPLogger:
    """Logs HTTP requests and responses."""
    async def log_request(
        self,
        request: web.Request
    ) -> str:
        """Assigns special uuid to request and logs it.

        Args:
            request:
                Request to be logged.

        Returns:
            Request assigned UUID.
        """
        plain_message: str = \
            f"request {request.method.upper()} {request.url.path}" \
            f"{request.url.query}"

        request_uuid: str = rnd.gen_uuid()

        json_: Optional[dict] = None
        with contextlib.suppress(json.JSONDecodeError):
            # FIXME: hangs here, using request.body hangs too, see:
            #   https://github.com/encode/starlette/issues/847
            # json_ = validation.apply(await request.json(), dict)
            #
            # Seems like for now no request json will be collected until
            # mentioned issue is resolved.
            json_ = None
        if not json_:
            json_ = None

        extra: dict = dict(
            type="request",
            uuid=request_uuid,
            # Get full URL
            url=request.url._url,
            headers=dict(request.headers),
            json=json_
        )

        Log.bind(**extra).info(plain_message)

        return request_uuid

    async def log_response(
        self,
        response: web.Response,
        *,
        request: web.Request,
        request_uuid: str
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
            # response_body = response.body.decode()

        plain_message: str = \
            f"response {response.status_code}" \
            f" {request.url.path}{request.url.query}:" \
            f" {response_body}"
        json_: Optional[dict]
        json_ = validation.apply(
            json.loads(
                response_body
            ),
            dict
        )
        if not json_:
            json_ = None

        extra: dict = dict(
            type="response",
            status_code=response.status_code,
            request_uuid=request_uuid,
            media_type=response.media_type,
            headers=dict(response.headers),
            json=json_
        )

        Log.bind(**extra).info(plain_message)

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
