import pytest
from pykit.check import check
from pykit.fcode import code
from rxcat import OkEvt, PubOpts, Req, ServerBus

from orwynn.mongo import filter_collection_factory
from orwynn.sys import Sys


@code("mongo_no_collections_test_req")
class _Req1(Req):
    collection: str

class _Sys1(Sys):
    CommonSubMsgFilters = [
        filter_collection_factory("hello")]

    async def init(self):
        await self._sub(_Req1, self._on_req1)

    async def _on_req1(self, req: _Req1):
        await self._pub(OkEvt(rsid="").as_res_from_req(req))

@pytest.mark.asyncio
async def test_has_collection(app):
    bus = ServerBus.ie()
    evt = await bus.pubr(_Req1(collection="hello"))
    assert isinstance(evt, OkEvt)

@pytest.mark.asyncio
async def test_no_collection(app):
    bus = ServerBus.ie()
    await check.aexpect(
        bus.pubr(_Req1(collection="whocares"), PubOpts(pubr_timeout=0.001)),
        TimeoutError)
