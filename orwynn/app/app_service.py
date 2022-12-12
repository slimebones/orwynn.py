from fastapi import FastAPI
from starlette.types import Scope, Receive, Send
from orwynn.app.app_mode import AppMode
from orwynn.base.service.framework_service import FrameworkService
from orwynn.base.test.test_client import TestClient


class AppService(FrameworkService):
    def __init__(self) -> None:
        super().__init__()
        self._app: FastAPI = FastAPI()

    async def __call__(
        self, scope: Scope, receive: Receive, send: Send
    ) -> None:
        await self._app(scope, receive, send)

    @property
    def test_client(self) -> TestClient:
        raise

    @property
    def root_dir(self) -> str:
        raise

    @property
    def mode_enum(self) -> AppMode:
        raise
