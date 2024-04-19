from pykit.check import check
from pykit.err import LockErr
from pykit.query import Query

from orwynn.mongo import Doc


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

