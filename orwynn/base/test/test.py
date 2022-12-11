from pytest import fixture

from orwynn.app.app_service import AppService
from orwynn.base.test.http_client import HttpClient
from orwynn.base.test.test_client import TestClient


class Test:
    @fixture
    def http(self, client: TestClient) -> HttpClient:
        return HttpClient(client)

    # TODO:
    #   Find way how to fetch user's test Boot object with his RootModule
    #   inserted.
    #
    # @fixture
    # def app(self) -> AppService:
    #     return boot.app

    @fixture
    def client(self, app: AppService) -> TestClient:
        return app.test_client

    @fixture
    def root_dir(self, app: AppService) -> str:
        return app.root_dir
