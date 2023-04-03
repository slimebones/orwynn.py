from orwynn.apiversion import ApiVersion
from orwynn.app import App
from orwynn.base import Module
from orwynn.boot import Boot


def create_root_module() -> Module:
    return Module(
        "/",
        Providers=[],
        Controllers=[],
        imports=[
        ]
    )


def create_boot() -> Boot:
    return Boot(
        create_root_module(),
        global_http_route="/api/v{version}",
        global_websocket_route="/ws/v{version}",
        api_version=ApiVersion(supported={1}),
    )


def create_app() -> App:
    return create_boot().app
