from pytest import fixture

from orwynn.app._App import App
from orwynn.boot._Boot import Boot


@fixture
def std_app(std_boot: Boot) -> App:
    return std_boot.app


def test_openapi(run_endpoint):
    data: dict = Boot.ie().app.client.get_jsonify("/openapi.json", 200)

    path: dict = data["paths"]["/"]["get"]
    assert path["deprecated"] is True
    assert path["tags"] == ["best-item", "buy-now"]
    assert \
        path["responses"]["201"]["description"] == "Best response description"
    assert \
        path["responses"]["201"]["description"] == "Best response description"
