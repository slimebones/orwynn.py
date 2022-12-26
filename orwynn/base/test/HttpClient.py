import inspect
from types import NoneType
from typing import Any, Callable, TypeVar

from orwynn.base.test.TestClient import TestClient
from orwynn.util.validation import validate
from orwynn.util.web import TestResponse

# If ever you get to Python3.12, see if PEP 696 introduced, then apply
# ... = TypeVar("...", default=dict)
# but for now it is in the next form
_JsonifyExpectedType = TypeVar("_JsonifyExpectedType")


class HttpClient:
    """Operates with HTTP client requests for test purposes."""
    def __init__(self, client: TestClient) -> None:
        self._client: TestClient = client

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
        request: str = ' '.join([stack[0][3], url])
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
        url: str

        validate(request, str)
        validate(asserted_status_code, [int, NoneType])

        # Request example: 'get /users/1'
        method, url = request.split(' ')

        # Also can accept uppercase 'GET ...'
        method = method.lower()

        match method:
            case "get":
                test_client_method = self._client.get
            case "post":
                test_client_method = self._client.post
            case "delete":
                test_client_method = self._client.delete
            case "put":
                test_client_method = self._client.put
            case "patch":
                test_client_method = self._client.patch
            case "options":
                test_client_method = self._client.options
            case _:
                raise ValueError(f'Method {method} is not supported')

        response: TestResponse = test_client_method(url, **request_kwargs)

        validate(response, TestResponse, is_strict=True)

        if asserted_status_code is not None:
            assert \
                response.status_code == asserted_status_code, \
                f"response status code {response.status_code}" \
                f" != asserted status code {asserted_status_code};" \
                f" response content is {response.content}"

        return response
