from pykit.check import check

from orwynn.mongo import Doc, Query
from orwynn.mongo.field import DocField, UniqueFieldErr


class _Doc1(Doc):
    FIELDS = [
        DocField(
            name="name",
            unique=True
        )
    ]
    name: str

class _Doc2(Doc):
    FIELDS = [
        DocField(
            name="doc1_sids",
            linked_doc="_doc1")
    ]

    doc1_sids: list[str] = []

def test_unique_create(app):
    _Doc1(name="pizza").create()
    check.expect(_Doc1(name="pizza").create, UniqueFieldErr)
    assert len(list(_Doc1.get_many())) == 1

def test_unique_upd(app):
    d1 = _Doc1(name="pizza").create()
    d2 = _Doc1(name="notpizza").create()

    check.expect(d2.upd, UniqueFieldErr, Query.as_upd(set={"name": "pizza"}))
    assert len(list(_Doc1.get_many())) == 2

    d1 = d1.refresh()
    d2 = d2.refresh()
    assert d1.name == "pizza"
    assert d2.name == "notpizza"

def test_links(app):
    d1 = _Doc1(name="pizza").create()
    d2 = _Doc1(name="donut").create()
    dh = _Doc2(doc1_sids=[d1.sid, d2.sid]).create()
    print(d1.get_collection())

    d1.delete()
    d1.refresh().del_archived()
    dh = dh.refresh()

    assert dh.doc1_sids == [d2.sid]

