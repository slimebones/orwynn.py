import pytest

from orwynn.base.module.module import Module
from orwynn.boot.boot import Boot
from orwynn.http import Endpoint, HttpController
from orwynn.utils import validation

from . import ApiVersion
from .errors import UnsupportedVersionError

# NOTE: By default there is no global route for backwards compatiblity.

@pytest.mark.asyncio
async def test_versioned_global_route():
    class C(HttpController):
        Route = "/message"
        Endpoints = [Endpoint(method="get")]

        def get(self) -> dict:
            return {"message": "hello"}

    boot: Boot = await Boot.create(
        root_module=Module("/user", Controllers=[C]),
        global_http_route="/donuts/v{version}",
    )

    boot.app.client.get_jsonify(
        "/donuts/v1/user/message",
        200,
        is_global_route_used=False
    )


@pytest.mark.asyncio
async def test_controller_version():
    """
    HttpController can define older version of API than available.
    """
    class C1(HttpController):
        Route = "/message"
        Version = 1
        Endpoints = [Endpoint(method="get")]

        def get(self) -> dict:
            return {"message": "hello v1"}

    class C2(HttpController):
        # Here we don't need to define a Version, since the v2 should be
        # latest.
        Route = "/message"
        Endpoints = [Endpoint(method="get")]

        def get(self) -> dict:
            return {"message": "hello v2"}

    boot: Boot = await Boot.create(
        root_module=Module("/user", Controllers=[C1, C2]),
        global_http_route="/api/v{version}",
        api_version=ApiVersion(
            supported={1, 2}
        )
    )

    data: dict

    data = boot.app.client.get_jsonify(
        "/user/message", 200, api_version=1
    )
    assert data["message"] == "hello v1"

    data = boot.app.client.get_jsonify(
        "/user/message", 200, api_version=2
    )
    assert data["message"] == "hello v2"

    data = boot.app.client.get_jsonify(
        "/api/v3/user/message", 404, is_global_route_used=False
    )


@pytest.mark.asyncio
async def test_controller_all_versions():
    class C1(HttpController):
        Route = "/message"
        Version = "*"
        Endpoints = [Endpoint(method="get")]

        def get(self) -> dict:
            return {"message": "hello"}

    boot: Boot = await Boot.create(
        root_module=Module("/user", Controllers=[C1]),
        global_http_route="/api/v{version}",
        api_version=ApiVersion(
            supported={1, 2, 3}
        )
    )

    data: dict

    data = boot.app.client.get_jsonify("/user/message", 200, api_version=1)
    assert data["message"] == "hello"

    data = boot.app.client.get_jsonify("/user/message", 200, api_version=2)
    assert data["message"] == "hello"

    data = boot.app.client.get_jsonify("/user/message", 200, api_version=3)
    assert data["message"] == "hello"


@pytest.mark.asyncio
async def test_controller_several_versions():
    class C1(HttpController):
        Route = "/message"
        Version = {2, 3}
        Endpoints = [Endpoint(method="get")]

        def get(self) -> dict:
            return {"message": "hello"}

    boot: Boot = await Boot.create(
        root_module=Module("/user", Controllers=[C1]),
        global_http_route="/api/v{version}",
        api_version=ApiVersion(
            supported={1, 2, 3}
        )
    )

    data: dict

    data = boot.app.client.get_jsonify("/user/message", 404, api_version=1)

    data = boot.app.client.get_jsonify("/user/message", 200, api_version=2)
    assert data["message"] == "hello"

    data = boot.app.client.get_jsonify("/user/message", 200, api_version=3)
    assert data["message"] == "hello"


@pytest.mark.asyncio
async def test_controller_unsupported_version():
    class C1(HttpController):
        Route = "/message"
        Version = 3
        Endpoints = [Endpoint(method="get")]

        def get(self) -> dict:
            return {"message": "hello"}

    await validation.expect_async(
        Boot.create(
            root_module=Module("/user", Controllers=[C1]),
            global_http_route="/api/v{version}",
            api_version=ApiVersion(
                supported={1, 2}
            )
        ),
        UnsupportedVersionError
    )


@pytest.mark.asyncio
async def test_controller_unsupported_version_of_many():
    class C1(HttpController):
        Route = "/message"
        # Some are supported, some are not
        Version = {2, 3}
        Endpoints = [Endpoint(method="get")]

        def get(self) -> dict:
            return {"message": "hello"}

    await validation.expect_async(
        Boot.create(
            root_module=Module("/user", Controllers=[C1]),
            global_http_route="/api/v{version}",
            api_version=ApiVersion(
                supported={1, 2}
            )
        ),
        UnsupportedVersionError
    )
