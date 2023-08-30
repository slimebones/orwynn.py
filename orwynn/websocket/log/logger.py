from orwynn.log import Log
from orwynn.utils import validation
from orwynn.websocket.websocket import Websocket


class WebsocketLogger:
    """Logs websocket requests."""
    async def log_request(
        self,
        request: Websocket,
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
        validation.validate(request, Websocket)
        validation.validate(request_id, str)

        plain_message: str = \
            f"websocket CONNECT {request.url.path}" \
            f"{request.url.query}"

        extra: dict = {
            "websocket.request": {
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

    async def log_response(
        self,
        response_data: dict,
        *,
        request: Websocket,
        request_id: str
    ) -> None:
        """
        Logs a response linking it to the according request.
        """
        plain_message: str = \
            "websocket response" \
            f" {request.url.path}{request.url.query}:" \
            f" {response_data}"

        extra: dict = {
            "websocket.response": {
                "request_id": request_id,
                "json": response_data
            }
        }

        Log.bind(**extra).info(
            plain_message
        )
