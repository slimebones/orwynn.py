from orwynn.base.controller.controller import Controller
from orwynn.http.http import HTTPMethod


def test_http_methods():
    for method in HTTPMethod:
        assert hasattr(Controller, method.value)
