import inspect
from types import NoneType
from typing import TYPE_CHECKING, Any, Callable, Optional, Self, TypeVar
from orwynn.apiversion import ApiVersion
from orwynn.base.model.model import Model
from orwynn.proxy.boot import BootProxy

from orwynn.testing.embeddedclient import EmbeddedTestClient
from orwynn.utils import validation
from orwynn.utils.validation import validate
from orwynn.utils.scheme import Scheme
from orwynn.utils.url import join_routes

if TYPE_CHECKING:
    from orwynn.http import TestHttpResponse

# If ever you get to Python3.12, see if PEP 696 introduced, then apply
# but for now it is in the next form
_JsonifyExpectedType = TypeVar("_JsonifyExpectedType")


class _FinalizedRequestData(Model):
    route: str
    kwargs: dict


class Client:
    """
    Operates with HTTP client requests for test purposes.
    """
    def __init__(
        self,
        embedded_client: EmbeddedTestClient,
        *,
        binded_headers: dict[str, str] | None = None
    ) -> None:
        validation.validate(embedded_client, EmbeddedTestClient)
        self._embedded_client: EmbeddedTestClient = embedded_client

        if binded_headers is None:
            binded_headers = {}
        # Do copy here again for an additional safety, although headers copying
        # is already done at bind_headers() method.
        self._binded_headers: dict[str, str] = binded_headers.copy()

    @property
    def binded_headers(self) -> dict:
        return self._binded_headers

    def bind_headers(
        self,
        headers: dict[str, str]
    ) -> Self:
        validation.validate_dict(headers, (str, str))

        # Accumulate headers from this client to the new one.
        #
        # Also copy binded headers to not stack them after multiple
        # bind_headers() calls.
        final_headers: dict[str, str] = self._binded_headers.copy()
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
        r: "TestHttpResponse" = self.get(url, asserted_status_code, **kwargs)
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
        r: "TestHttpResponse" = self.post(url, asserted_status_code, **kwargs)
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
        r: "TestHttpResponse" = self.delete(
            url, asserted_status_code, **kwargs
        )
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
        r: "TestHttpResponse" = self.put(url, asserted_status_code, **kwargs)
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
        r: "TestHttpResponse" = self.patch(url, asserted_status_code, **kwargs)
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
        r: "TestHttpResponse" = self.options(
            url, asserted_status_code, **kwargs
        )
        data: Any = r.json()
        validate(data, expected_type)
        return data

    def get(
        self,
        url: str,
        asserted_status_code: int | None = None,
        **kwargs
    ) -> "TestHttpResponse":
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
    ) -> "TestHttpResponse":
        return self._get_test_response(
            inspect.stack(), url, asserted_status_code, **kwargs)

    def delete(
        self,
        url: str,
        asserted_status_code: int | None = None,
        **kwargs
    ) -> "TestHttpResponse":
        return self._get_test_response(
            inspect.stack(), url, asserted_status_code, **kwargs)

    def put(
        self,
        url: str,
        asserted_status_code: int | None = None,
        **kwargs
    ) -> "TestHttpResponse":
        return self._get_test_response(
            inspect.stack(), url, asserted_status_code, **kwargs)

    def patch(
        self,
        url: str,
        asserted_status_code: int | None = None,
        **kwargs
    ) -> "TestHttpResponse":
        return self._get_test_response(
            inspect.stack(), url, asserted_status_code, **kwargs)

    def options(
        self,
        url: str,
        asserted_status_code: int | None = None,
        **kwargs
    ) -> "TestHttpResponse":
        return self._get_test_response(
            inspect.stack(), url, asserted_status_code, **kwargs)

    def _get_test_response(
        self,
        stack: list[inspect.FrameInfo],
        url: str,
        asserted_status_code: int | None,
        **kwargs
    ) -> "TestHttpResponse":
        request: str = " ".join([stack[0][3], url])
        return self._resolve_request(request, asserted_status_code, **kwargs)

    def _resolve_request(
        self,
        request: str,
        asserted_status_code: int | None,
        **request_kwargs
    ) -> "TestHttpResponse":
        response: "TestHttpResponse"
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

        # Get finalized data
        finalized: _FinalizedRequestData = self._process_request_data(
            route=route,
            request_kwargs=request_kwargs,
            protocol=Scheme.HTTP
        )

        # Make a request
        response: "TestHttpResponse" = test_client_method(
            finalized.route,
            **finalized.kwargs
        )

        if asserted_status_code is not None:
            assert \
                response.status_code == asserted_status_code, \
                f"response status code {response.status_code}" \
                f" != asserted status code {asserted_status_code};" \
                f" response content is {response.content}"

        return response

    def _process_request_data(
        self,
        *,
        route: str,
        request_kwargs: dict,
        protocol: Scheme
    ) -> _FinalizedRequestData:
        """
        Processes a given route and request kwargs and returns finalized
        versions of them.
        """
        request_kwargs = request_kwargs.copy()

        # Add binded headers
        request_kwargs.setdefault("headers", {})
        request_kwargs["headers"].update(self._binded_headers)

        # Craft the final route
        is_global_route_used: bool = validation.apply(
            request_kwargs.get("is_global_route_used", True),
            bool
        )
        api_version: int | None = request_kwargs.get("api_version", None)
        validation.validate(api_version, [int, NoneType])
        final_route: str = self._get_final_route(
            route,
            is_global_route_used=is_global_route_used,
            api_version=api_version,
            protocol=protocol
        )
        # Delete custom keys to not confuse a client's method
        try:
            del request_kwargs["is_global_route_used"]
        except KeyError:
            pass
        try:
            del request_kwargs["api_version"]
        except KeyError:
            pass

        return _FinalizedRequestData(
            route=final_route,
            kwargs=request_kwargs
        )

    def _get_final_route(
        self,
        route: str,
        *,
        is_global_route_used: bool,
        api_version: int | None,
        protocol: Scheme
    ) -> str:
        if not is_global_route_used and api_version is not None:
            raise ValueError(
                f"the global route is disabled and api version is also passed"
                " which doesn't make sense"
            )
        elif not is_global_route_used:
            return route

        api_version_obj: ApiVersion = BootProxy.ie().api_version

        global_route: str = BootProxy.ie().get_global_route_for_protocol(
            protocol
        )

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

        return join_routes(
            final_global_route,
            route
        )

    def websocket(
        self,
        route: str,
        **request_kwargs
    ) -> Any:
        finalized: _FinalizedRequestData = self._process_request_data(
            route=route,
            request_kwargs=request_kwargs,
            protocol=Scheme.WEBSOCKET
        )

        return self._embedded_client.websocket_connect(
            finalized.route,
            **finalized.kwargs
        )
