from orwynn import validation
from orwynn.boot.Boot import Boot
from orwynn.boot.api_version.ApiVersion import ApiVersion
from orwynn.boot.api_version.UnsupportedVersionError import UnsupportedVersionError
from orwynn.controller.Controller import Controller
from orwynn.controller.endpoint.Endpoint import Endpoint
from orwynn.module.Module import Module



# NOTE: By default there is no global route for backwards compatiblity.

def test_versioned_global_route():
    class C(Controller):
        ROUTE = "/message"
        ENDPOINTS = [Endpoint(method="get")]

        def get(self) -> dict:
            return {"message": "hello"}

    boot: Boot = Boot(
        root_module=Module("/user", Controllers=[C]),
        global_route="/donuts/{version}",
    )

    boot.app.client.get_jsonify("/donuts/v1/user/message", 200)


def test_controller_version():
    # Controller can define older version of API than available.
    #
    class C1(Controller):
        ROUTE = "/message"
        VERSION = 1
        ENDPOINTS = [Endpoint(method="get")]

        def get(self) -> dict:
            return {"message": "hello v1"}

    class C2(Controller):
        # Here we don't need to define a VERSION, since the v2 should be most
        # recent.
        ROUTE = "/message"
        ENDPOINTS = [Endpoint(method="get")]

        def get(self) -> dict:
            return {"message": "hello v2"}

    boot: Boot = Boot(
        root_module=Module("/user", Controllers=[C1, C2]),
        global_route="/api/{version}",
        api_version=ApiVersion(
            supported={1, 2}
        )
    )

    data: dict

    data = boot.app.client.get_jsonify("/api/v1/user/message", 200)
    assert data["value"]["message"] == "hello v1"

    data = boot.app.client.get_jsonify("/api/v2/user/message", 200)
    assert data["value"]["message"] == "hello v2"

    data = boot.app.client.get_jsonify("/api/v3/user/message", 404)


def test_controller_all_versions():
    class C1(Controller):
        ROUTE = "/message"
        VERSION = "all"
        ENDPOINTS = [Endpoint(method="get")]

        def get(self) -> dict:
            return {"message": "hello"}

    boot: Boot = Boot(
        root_module=Module("/user", Controllers=[C1]),
        global_route="/api/{version}",
        api_version=ApiVersion(
            supported={1, 2, 3}
        )
    )

    data: dict

    data = boot.app.client.get_jsonify("/api/v1/user/message", 200)
    assert data["value"]["message"] == "hello"

    data = boot.app.client.get_jsonify("/api/v2/user/message", 200)
    assert data["value"]["message"] == "hello"

    data = boot.app.client.get_jsonify("/api/v3/user/message", 200)
    assert data["value"]["message"] == "hello"


def test_controller_several_versions():
    class C1(Controller):
        ROUTE = "/message"
        VERSION = {2, 3}
        ENDPOINTS = [Endpoint(method="get")]

        def get(self) -> dict:
            return {"message": "hello"}

    boot: Boot = Boot(
        root_module=Module("/user", Controllers=[C1]),
        global_route="/api/{version}",
        api_version=ApiVersion(
            supported={1, 2, 3}
        )
    )

    data: dict

    data = boot.app.client.get_jsonify("/api/v1/user/message", 404)

    data = boot.app.client.get_jsonify("/api/v2/user/message", 200)
    assert data["value"]["message"] == "hello"

    data = boot.app.client.get_jsonify("/api/v3/user/message", 200)
    assert data["value"]["message"] == "hello"


def test_controller_unsupported_version():
    class C1(Controller):
        ROUTE = "/message"
        VERSION = 3
        ENDPOINTS = [Endpoint(method="get")]

        def get(self) -> dict:
            return {"message": "hello"}

    validation.expect(
        Boot,
        UnsupportedVersionError,
        root_module=Module("/user", Controllers=[C1]),
        global_route="/api/{version}",
        api_version=ApiVersion(
            supported={1, 2}
        )
    )


def test_controller_unsupported_version_of_many():
    class C1(Controller):
        ROUTE = "/message"
        # Some are supported, some are not
        VERSION = {2, 3}
        ENDPOINTS = [Endpoint(method="get")]

        def get(self) -> dict:
            return {"message": "hello"}

    validation.expect(
        Boot,
        UnsupportedVersionError,
        root_module=Module("/user", Controllers=[C1]),
        global_route="/api/{version}",
        api_version=ApiVersion(
            supported={1, 2}
        )
    )
