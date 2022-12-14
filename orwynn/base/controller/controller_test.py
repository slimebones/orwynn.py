from orwynn.base.controller.controller import Controller
from orwynn.boot.boot import Boot
from orwynn.http.http import HTTPMethod


def test_http_methods():
    for method in HTTPMethod:
        assert hasattr(Controller, method.value)


def test_std_routes(std_boot: Boot):
    pass
