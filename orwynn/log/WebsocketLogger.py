

from orwynn import validation, web
from orwynn.log.Log import Log


class WebsocketLogger:
    """Logs websocket requests."""
    async def log_request(
        self,
        request: web.Websocket,
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
        validation.validate(request, web.Websocket)
        validation.validate(request_id, str)

        plain_message: str = \
            f"websocket CONNECT {request.url.path}" \
            f"{request.url.query}"

        extra: dict = {
            "websocket": {
                "id": request_id,
                # Get full URL
                "url": request.url._url,
                "headers": dict(request.headers)
            }
        }

        Log.bind(**extra).info(
            plain_message
        )

        return request_id
