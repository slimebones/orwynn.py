from typing import Literal
from fastapi import FastAPI
from starlette.types import Scope, Receive, Send
from fastapi.testclient import TestClient
from orwynn.src.app.app_mode_enum import AppModeEnum
from orwynn.src.base.service.root_service import RootService


class AppService(RootService):
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
    def mode_enum(self) -> AppModeEnum:
        raise