from pytest import fixture

from orwynn.app.AppService import AppService
from orwynn.boot.Boot import Boot


@fixture
def std_app(std_boot: Boot) -> AppService:
    return std_boot.app


def test_openapi(run_endpoint):
    data: dict = Boot.ie().app.http_client.get_jsonify("/openapi.json", 200)

    path: dict = data["paths"]["/"]["get"]
    assert path["deprecated"] is True
    assert path["tags"] == ["best-item", "buy-now"]
    assert \
        path["responses"]["201"]["description"] == "Best response description"
    assert \
        path["responses"]["201"]["description"] == "Best response description"

    assert False
