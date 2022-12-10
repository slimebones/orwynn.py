from pytest import fixture
from orwynn.app.app_mode_enum import AppModeEnum

from orwynn.app.app_service import AppService
from orwynn.base.module.root_module import RootModule
from orwynn.base.test.http_client import HttpClient
from orwynn.base.test.test_client import TestClient
from orwynn.boot.boot import Boot
from orwynn.di.di import DI


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
