from typing import Any, Callable, Sequence

from fastapi import params
from fastapi.dependencies.utils import get_parameterless_sub_dependant
from fastapi.routing import APIWebSocketRoute as _NativeWebsocketRoute
from fastapi.routing import get_websocket_app
from starlette.routing import (
    compile_path,
    get_name,
    websocket_session,
)

from orwynn.app.utils import get_dependant


class ApiWebsocketRoute(_NativeWebsocketRoute):
    def __init__(
        self,
        path: str,
        endpoint: Callable[..., Any],
        *,
        name: str | None = None,
        dependencies: Sequence[params.Depends] | None = None,
        dependency_overrides_provider: Any | None = None,
    ) -> None:
        # Copy of FastAPI code for APIWebSocket route to fix dependants issue
        # for customized websocket middleware
        #
        self.path = path
        self.endpoint = endpoint
        self.name = get_name(endpoint) if name is None else name
        self.dependencies = list(dependencies or [])
        self.path_regex, self.path_format, self.param_convertors = \
            compile_path(path)

        # Here get_dependant is our function. Due to unknown reason we haven't
        # managed to do the replacement via mock (as we did with ApiRouter for
        # example), so here we copied the entire init function body to replace
        # the function directly
        self.dependant = get_dependant(
            path=self.path_format, call=self.endpoint
        )

        for depends in self.dependencies[::-1]:
            self.dependant.dependencies.insert(
                0,
                get_parameterless_sub_dependant(
                    depends=depends,
                    path=self.path_format
                )
            )

        self.app = websocket_session(
            get_websocket_app(
                dependant=self.dependant,
                dependency_overrides_provider=dependency_overrides_provider,
            )
        )
