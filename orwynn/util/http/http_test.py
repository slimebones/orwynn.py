from pytest import fixture

from orwynn.app.AppService import AppService
from orwynn.base.test.http_client import HttpClient


@fixture
def std_http(std_app: AppService) -> HttpClient:
    return HttpClient(std_app.test_client)
