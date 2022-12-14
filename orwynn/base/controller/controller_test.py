from orwynn.base.controller.controller import Controller


def test_http_methods():
    for method in ["get", "post", "put", "delete", "patch", "options"]:
        assert hasattr(Controller, method)
