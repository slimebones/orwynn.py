from pytest import fixture

from orwynn.app.AppService import AppService
from orwynn.base.test.HttpClient import HttpClient
from orwynn.boot.Boot import Boot


@fixture
def std_app(std_boot: Boot) -> AppService:
    return std_boot.app


def test_openapi__std(std_app: AppService, std_http: HttpClient):
    std_http.get("/openapi.json")
