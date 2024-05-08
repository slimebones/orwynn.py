import typing

import pytest
from pykit.check import check
from pykit.err import LockErr
from pykit.query import Query
from rxcat import OkEvt, ServerBus

from orwynn.mongo import CheckLockDocReq, Doc, LockDocReq, UnlockDocReq
from orwynn.msg import FlagEvt


def test_lock_write(app):
    class TestLockDoc(Doc):
        name: str

    d = TestLockDoc(name="hello").create()
    d = d.lock()

    check.expect(d.upd, LockErr, Query.as_upd(set={"name": "wow"}))
    check.expect(d.delete, LockErr)
    check.expect(d.get_and_del, LockErr, Query({"sid": d.sid}))
    check.expect(
        d.get_and_upd,
        LockErr,
        Query({"sid": d.sid}),
        Query.as_upd(set={"name": "wow"}))

    assert not d.try_upd(Query.as_upd(set={"name": "wow"}))
    assert not d.try_del()
    assert not d.try_get_and_del(Query({"sid": d.sid}))

    d = d.unlock()

    assert d.upd(Query.as_upd(set={"name": "world"})).name == "world"
    assert d.try_upd(Query.as_upd(set={"name": "wow"}))
    d.delete()
    assert not d.try_get(Query({"sid": d.sid}))

@pytest.mark.asyncio
async def test_sys(app):
    class TestLockSysDoc(Doc):
        COLLECTION_NAMING = "snake_case"
        name: str

    doc = TestLockSysDoc(name="hello").create()
    bus = ServerBus.ie()

    evt = await bus.pubr(
        LockDocReq(doc_collection="test_lock_sys_doc", doc_sid=doc.sid))
    assert isinstance(evt, OkEvt)
    assert "locked" in doc.refresh().internal_marks

    evt = await bus.pubr(CheckLockDocReq(
        doc_collection="test_lock_sys_doc", doc_sid=doc.sid))
    assert isinstance(evt, FlagEvt)
    assert typing.cast(FlagEvt, evt).val is True

    evt = await bus.pubr(
        UnlockDocReq(doc_collection="test_lock_sys_doc", doc_sid=doc.sid))
    assert isinstance(evt, OkEvt)
    assert "locked" not in doc.refresh().internal_marks

    evt = await bus.pubr(CheckLockDocReq(
        doc_collection="test_lock_sys_doc", doc_sid=doc.sid))
    assert isinstance(evt, FlagEvt)
    assert typing.cast(FlagEvt, evt).val is False

