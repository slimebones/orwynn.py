from typing import Literal
from fastapi.testclient import TestClient
from orwynn.src.app.app_mode_enum import AppModeEnum
from orwynn.src.base.service.root_service import RootService


class AppService(RootService):
    @property
    def test_client(self) -> TestClient:
        raise

    @property
    def root_dir(self) -> str:
        raise

    @property
    def mode_enum(self) -> AppModeEnum:
        raise