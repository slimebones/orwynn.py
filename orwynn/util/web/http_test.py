from pytest import fixture

from orwynn.test.Client import Client


@fixture
def std_http(std_app) -> Client:
    return std_app.client
