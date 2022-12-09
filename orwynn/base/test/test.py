from fastapi import FastAPI
from pytest import fixture
from fastapi.testclient import TestClient
from orwynn.src.app.app_mode_enum import AppModeEnum

from orwynn.src.app.app_service import AppService
from orwynn.src.base.module.root_module import RootModule
from orwynn.src.base.test.http_client import HttpClient
from orwynn.src.boot.boot import Boot
from orwynn.src.di.di import DI


class Test:
    @fixture
    def http(self, client: TestClient) -> HttpClient:
        return HttpClient(client)

    @fixture
    def app(self) -> AppService:
        return DI.ie().find("app_service")

    @fixture
    def client(self, app: AppService) -> TestClient:
        return app.test_client

    @fixture
    def root_dir(self, app: AppService) -> str:
        return app.root_dir
