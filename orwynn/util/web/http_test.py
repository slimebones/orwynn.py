from pytest import fixture

from orwynn.base.test.HttpClient import HttpClient


@fixture
def std_http(std_app) -> HttpClient:
    return HttpClient(std_app.test_client)
