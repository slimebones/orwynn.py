from pytest import fixture

from orwynn.app.AppService import AppService
from orwynn.base.test.test_client import TestClient


class Test:
    pass
    # @fixture
    # def http(self, client: TestClient) -> HttpTestClient:
    #     return HttpTestClient(client)

    # TODO:
    #   Find way how to fetch user's test Boot object with his RootModule
    #   inserted.
    #
    # @fixture
    # def app(self) -> AppService:
    #     return boot.app
