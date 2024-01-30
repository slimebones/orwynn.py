from typing import Any
import uvicorn
from orwynn.boot.boot import Boot
from orwynn.helpers.errors import UnsupportedError
from orwynn.server.engine import ServerEngine


class Server:
    """
    Serves the application.

    For now the sole option available - serving via Uvicorn. In future the
    option list might be extended.

    Args:
        engine:
            Underlying server to use.
        boot:
            Orwynn Boot instance.
    """
    def __init__(
        self,
        *,
        engine: ServerEngine,
        boot: Boot
    ) -> None:
        self._engine: ServerEngine = engine
        self._boot: Boot = boot

    async def serve(
        self,
        *,
        host: str,
        port: int
    ) -> None:
        """
        Serves the application from given at initialization Boot instance and
        selected underlying engine.

        Args:
            host:
                Host to serve on.
            port:
                Port to serve on.
        """
        await self._get_core_server(
            host=host,
            port=port
        ).serve()

    def _get_core_server(
        self,
        *,
        host: str,
        port: int
    ) -> Any:
        match self._engine:
            case ServerEngine.Uvicorn:
                return self._get_uvicorn_server(
                    host=host,
                    port=port
                )
            case _:
                raise UnsupportedError(
                    title="server engine",
                    value=self._engine
                )

    def _get_uvicorn_server(
        self,
        *,
        host: str,
        port: int
    ) -> uvicorn.Server:
        config: uvicorn.Config = uvicorn.Config(
            self._boot,
            host=host,
            port=port
        )

        return uvicorn.Server(config)
