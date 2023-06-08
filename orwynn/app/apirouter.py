from unittest.mock import patch

from fastapi.routing import APIRouter as _NativeApiRouter

from orwynn.app.apiwebsocketroute import ApiWebsocketRoute


class ApiRouter(_NativeApiRouter):
    def add_api_websocket_route(self, *args, **kwargs) -> None:
        with patch("fastapi.routing.APIWebSocketRoute", new=ApiWebsocketRoute):
            return super().add_api_websocket_route(*args, **kwargs)
