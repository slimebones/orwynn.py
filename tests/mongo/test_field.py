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
