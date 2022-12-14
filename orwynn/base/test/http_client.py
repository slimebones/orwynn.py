import inspect
from typing import Callable

from orwynn.http import TestResponse
from orwynn.base.test.test_client import TestClient

from orwynn.validation import validate


class HttpClient:
    """Operates with HTTP client requests for test purposes."""
    def __init__(self, client: TestClient) -> None:
        self._client: TestClient = client

    def get(
        self,
        url: str,
        asserted_status_code: int = 200,
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
        asserted_status_code: int = 200,
        **kwargs
    ) -> TestResponse:
        return self._get_test_response(
            inspect.stack(), url, asserted_status_code, **kwargs)

    def delete(
            self, url: str, asserted_status_code: int = 200,
            **kwargs) -> TestResponse:
        return self._get_test_response(
            inspect.stack(), url, asserted_status_code, **kwargs)

    def patch(
            self, url: str, asserted_status_code: int = 200,
            **kwargs) -> TestResponse:
        return self._get_test_response(
            inspect.stack(), url, asserted_status_code, **kwargs)

    def put(
        self,
        url: str,
        asserted_status_code: int = 200,
        **kwargs
    ) -> TestResponse:
        return self._get_test_response(
            inspect.stack(), url, asserted_status_code, **kwargs)

    def _get_test_response(
        self,
        stack: list[inspect.FrameInfo],
        url: str,
        asserted_status_code: int,
        **kwargs
    ) -> TestResponse:
        request: str = ' '.join([stack[0][3], url])
        return self._resolve_request(request, asserted_status_code, **kwargs)

    def _resolve_request(
        self,
        request: str,
        asserted_status_code: int,
        **request_kwargs
    ) -> TestResponse:
        response: TestResponse
        test_client_method: Callable
        method: str
        url: str

        validate(request, str)
        validate(asserted_status_code, int)

        # Request example: 'get /users/1'
        method, url = request.split(' ')

        # Also can accept uppercase 'GET ...'
        method = method.lower()

        match method:
            case 'get':
                test_client_method = self._client.get
            case 'post':
                test_client_method = self._client.post
            case 'put':
                test_client_method = self._client.put
            case 'patch':
                test_client_method = self._client.patch
            case 'delete':
                test_client_method = self._client.delete
            case _:
                raise ValueError(f'Method {method} is not supported')

        response = test_client_method(url, **request_kwargs)

        assert response.status_code == asserted_status_code, response.json

        return response
