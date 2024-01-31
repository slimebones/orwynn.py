from aiohttp import ClientResponse
from aiohttp.test_utils import TestClient as _AioTestClient


class Client:
    def __init__(self, native: _AioTestClient):
        self._native = native

    def ws(self, url: str = "/rx"):
        return self._native.ws_connect(url)

    async def post(
        self, url: str, asserted_status_code: int = 200, **kwargs
    ) -> ClientResponse:
        res = await self._native.post(url, **kwargs)
        res_text = await res.text()
        assert res.status == asserted_status_code, res_text
        return res

    async def post_jsonify(
        self,
        url: str,
        asserted_status_code: int = 200,
        **kwargs
    ) -> dict:
        res = await self.post(url, asserted_status_code, **kwargs)
        return await res.json()

