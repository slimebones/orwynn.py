import asyncio

import pytest
from fcode import code
from rxcat import Bus, Evt, InitdClientEvt, Req

from orwynn.tst import Client


@code("rxcat-test.msg1")
class _Evt1(Evt):
    num: int

@code("rxcat-test.msg2")
class _Evt2(Evt):
    num: int

@code("rxcat-test.req1")
class _Req1(Req):
    num: int

@code("rxcat-test.req2")
class _Req2(Req):
    num: int

@pytest.mark.asyncio
async def test_net_conn_and_pub(client: Client):
    bus = Bus.ie()
    arrived_msg = None

    async def on_msg1(msg1: _Evt1):
        nonlocal arrived_msg
        arrived_msg = msg1

    await bus.sub(_Evt1, on_msg1)

    async with client.ws("/rx") as ws:
        m = _Evt1(num=1)
        data: dict = await ws.receive_json()

        mcode = bus.try_get_mcode_for_mcodeid(data["mcodeid"])
        assert mcode == "pyrxcat.initd-client-evt"

        initd_evt = InitdClientEvt.deserialize_json(data)

        assert initd_evt.indexedMcodes
        assert initd_evt.indexedErrcodes

        m_mcodeid = bus.try_get_mcodeid_for_mtype(type(m))
        assert m_mcodeid is not None
        await ws.send_json(m.serialize_json(m_mcodeid))

        # wait for arrival
        await asyncio.sleep(0.0001)
        assert arrived_msg == m

