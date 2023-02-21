import inspect
from types import NoneType
from typing import Any, Callable, Optional, Self, TypeVar
from orwynn import web
from orwynn.boot.api_version.ApiVersion import ApiVersion
from orwynn.proxy.BootProxy import BootProxy

from orwynn.testing.EmbeddedTestClient import EmbeddedTestClient
from orwynn import validation
from orwynn.validation import validate
from orwynn.web import TestResponse

# If ever you get to Python3.12, see if PEP 696 introduced, then apply
# but for now it is in the next form
_JsonifyExpectedType = TypeVar("_JsonifyExpectedType")


class Client:
    """
    Operates with HTTP client requests for test purposes.
    """
    def __init__(
        self,
        embedded_client: EmbeddedTestClient,
        *,
        binded_headers: Optional[dict[str, Any]] = None
    ) -> None:
        validation.validate(embedded_client, EmbeddedTestClient)
        self._embedded_client: EmbeddedTestClient = embedded_client
        self.websocket = self._embedded_client.websocket_connect

        if binded_headers is None:
            binded_headers = {}
        self._binded_headers: dict[str, Any] = binded_headers

    @property
    def binded_headers(self) -> dict:
        return self._binded_headers

    def bind_headers(
        self,
        headers: dict[str, Any]
    ) -> Self:
        validation.validate_dict(headers, (str, validation.Validator.SKIP))

        # Accumulate headers from this client to the new one
        final_headers: dict[str, Any] = self._binded_headers
        final_headers.update(headers)

        return self.__class__(
            self._embedded_client,
            binded_headers=final_headers
        )

    def get_jsonify(
        self,
        url: str,
        asserted_status_code: int | None = None,
        *,
        expected_type: type[_JsonifyExpectedType] = dict,
        **kwargs
    ) -> _JsonifyExpectedType:
        r: TestResponse = self.get(url, asserted_status_code, **kwargs)
        data: Any = r.json()
        validate(data, expected_type)
        return data

    def post_jsonify(
        self,
        url: str,
        asserted_status_code: int | None = None,
        *,
        expected_type: type[_JsonifyExpectedType] = dict,
        **kwargs
    ) -> _JsonifyExpectedType:
        r: TestResponse = self.post(url, asserted_status_code, **kwargs)
        data: Any = r.json()
        validate(data, expected_type)
        return data

    def delete_jsonify(
        self,
        url: str,
        asserted_status_code: int | None = None,
        *,
        expected_type: type[_JsonifyExpectedType] = dict,
        **kwargs
    ) -> _JsonifyExpectedType:
        r: TestResponse = self.delete(url, asserted_status_code, **kwargs)
        data: Any = r.json()
        validate(data, expected_type)
        return data

    def put_jsonify(
        self,
        url: str,
        asserted_status_code: int | None = None,
        *,
        expected_type: type[_JsonifyExpectedType] = dict,
        **kwargs
    ) -> _JsonifyExpectedType:
        r: TestResponse = self.put(url, asserted_status_code, **kwargs)
        data: Any = r.json()
        validate(data, expected_type)
        return data

    def patch_jsonify(
        self,
        url: str,
        asserted_status_code: int | None = None,
        *,
        expected_type: type[_JsonifyExpectedType] = dict,
        **kwargs
    ) -> _JsonifyExpectedType:
        r: TestResponse = self.patch(url, asserted_status_code, **kwargs)
        data: Any = r.json()
        validate(data, expected_type)
        return data

    def options_jsonify(
        self,
        url: str,
        asserted_status_code: int | None = None,
        *,
        expected_type: type[_JsonifyExpectedType] = dict,
        **kwargs
    ) -> _JsonifyExpectedType:
        r: TestResponse = self.options(url, asserted_status_code, **kwargs)
        data: Any = r.json()
        validate(data, expected_type)
        return data

    def get(
        self,
        url: str,
        asserted_status_code: int | None = None,
        **kwargs
    ) -> TestResponse:
        # Join method name and function to call inner resolver
        # inspect.stack() is for resolving self method name, ref:
        #   https://stackoverflow.com/a/5067654
        return self._get_test_response(
            inspect.stack(), url, asserted_status_code, **kwargs)

    def post(
        self,
        url: str,
        asserted_status_code: int | None = None,
        **kwargs
    ) -> TestResponse:
        return self._get_test_response(
            inspect.stack(), url, asserted_status_code, **kwargs)

    def delete(
        self,
        url: str,
        asserted_status_code: int | None = None,
        **kwargs
    ) -> TestResponse:
        return self._get_test_response(
            inspect.stack(), url, asserted_status_code, **kwargs)

    def put(
        self,
        url: str,
        asserted_status_code: int | None = None,
        **kwargs
    ) -> TestResponse:
        return self._get_test_response(
            inspect.stack(), url, asserted_status_code, **kwargs)

    def patch(
        self,
        url: str,
        asserted_status_code: int | None = None,
        **kwargs
    ) -> TestResponse:
        return self._get_test_response(
            inspect.stack(), url, asserted_status_code, **kwargs)

    def options(
        self,
        url: str,
        asserted_status_code: int | None = None,
        **kwargs
    ) -> TestResponse:
        return self._get_test_response(
            inspect.stack(), url, asserted_status_code, **kwargs)

    def _get_test_response(
        self,
        stack: list[inspect.FrameInfo],
        url: str,
        asserted_status_code: int | None,
        **kwargs
    ) -> TestResponse:
        request: str = " ".join([stack[0][3], url])
        return self._resolve_request(request, asserted_status_code, **kwargs)

    def _resolve_request(
        self,
        request: str,
        asserted_status_code: int | None,
        **request_kwargs
    ) -> TestResponse:
        response: TestResponse
        test_client_method: Callable
        method: str
        route: str

        validate(request, str)
        validate(asserted_status_code, [int, NoneType])

        # Request example: "get /users/1"
        method, route = request.split(" ")

        # Also can accept uppercase "GET ..."
        method = method.lower()

        match method:
            case "get":
                test_client_method = self._embedded_client.get
            case "post":
                test_client_method = self._embedded_client.post
            case "delete":
                test_client_method = self._embedded_client.delete
            case "put":
                test_client_method = self._embedded_client.put
            case "patch":
                test_client_method = self._embedded_client.patch
            case "options":
                test_client_method = self._embedded_client.options
            case _:
                raise ValueError(f"Method {method} is not supported")

        # Add binded headers
        request_kwargs.setdefault("headers", {})
        request_kwargs["headers"].update(self._binded_headers)

        # Craft the final url
        is_global_route_used: bool = validation.apply(
            request_kwargs.get("is_global_route_used", True),
            bool
        )
        api_version: int | None = request_kwargs.get("api_version", None)
        validation.validate(api_version, [int, NoneType])
        final_url: str = self._get_final_url(
            route,
            is_global_route_used=is_global_route_used,
            api_version=api_version
        )
        # Delete custom keys to not confuse a client's method
        try:
            del request_kwargs["is_global_route_used"]
            del request_kwargs["api_version"]
        except KeyError:
            pass
        try:
            del request_kwargs["api_version"]
        except KeyError:
            pass

        # Make a request
        response: TestResponse = test_client_method(
            final_url,
            **request_kwargs
        )

        validate(response, TestResponse, is_strict=True)

        if asserted_status_code is not None:
            assert \
                response.status_code == asserted_status_code, \
                f"response status code {response.status_code}" \
                f" != asserted status code {asserted_status_code};" \
                f" response content is {response.content}"

        return response

    def _get_final_url(
        self,
        route: str,
        *,
        is_global_route_used: bool,
        api_version: int | None
    ) -> str:
        if not is_global_route_used and api_version is not None:
            raise ValueError(
                f"the global route is disabled and api version is also passed"
                " which doesn't make sense"
            )
        elif not is_global_route_used:
            return route

        api_version_obj: ApiVersion = BootProxy.ie().api_version
        global_route: str = BootProxy.ie().global_http_route
        final_api_version: int

        if api_version:
            final_api_version = api_version
        else:
            final_api_version = api_version_obj.latest

        final_global_route: str
        try:
            final_global_route = api_version_obj.apply_version_to_route(
                global_route,
                final_api_version
            )
        except ValueError:
            # No {version} format block
            final_global_route = global_route

        return web.join_routes(
            final_global_route,
            route
        )
