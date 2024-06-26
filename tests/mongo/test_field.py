from pykit.check import check
from pykit.query import UpdQuery

from orwynn.mongo import Doc, MongoUtils
from orwynn.mongo.field import DocField, UniqueFieldErr


class _Doc1(Doc):
    FIELDS = [
        DocField(
            name="name",
            unique=True
        )
    ]
    COLLECTION_NAMING = "snake_case"
    IS_ARCHIVABLE = True
    name: str

class _Doc2(Doc):
    FIELDS = [
        DocField(
            name="doc1_sids",
            linked_doc="_doc1")
    ]
    COLLECTION_NAMING = "snake_case"
    IS_ARCHIVABLE = True

    doc1_sids: list[str] = []

def test_unique_create(app):
    _Doc1(name="pizza").create()
    check.expect(_Doc1(name="pizza").create, UniqueFieldErr)
    assert len(list(_Doc1.get_many())) == 1

def test_unique_upd(app):
    d1 = _Doc1(name="pizza").create()
    d2 = _Doc1(name="notpizza").create()

    check.expect(
        d2.upd, UniqueFieldErr, UpdQuery.create(set={"name": "pizza"}))
    assert len(list(_Doc1.get_many())) == 2

    d1 = d1.refresh()
    d2 = d2.refresh()
    assert d1.name == "pizza"
    assert d2.name == "notpizza"

def test_links(app):
    d1 = _Doc1(name="pizza").create()
    d2 = _Doc1(name="donut").create()
    dh = _Doc2(doc1_sids=[d1.sid, d2.sid]).create()

    d1.delete()
    d1.refresh().del_archived()
    dh = dh.refresh()

    assert dh.doc1_sids == [d2.sid]

def test_links_multiple(app):
    class Doc1(Doc):
        COLLECTION_NAMING = "snake_case"
        FIELDS = [
            DocField(
                name="doc2_sids",
                linked_doc="doc2"),
            DocField(
                name="doc3_sids",
                linked_doc="doc3")]
        IS_ARCHIVABLE = True

        doc2_sids: list[str] = []
        doc3_sids: list[str] = []

    class Doc2(Doc):
        COLLECTION_NAMING = "snake_case"
        IS_ARCHIVABLE = True

    class Doc3(Doc):
        COLLECTION_NAMING = "snake_case"
        IS_ARCHIVABLE = True

    MongoUtils.register_doc_types(Doc1, Doc2, Doc3)

    d2_1 = Doc2().create()
    d2_2 = Doc2().create()
    d3_1 = Doc3().create()
    d3_2 = Doc3().create()
    d1_1 = Doc1(
        doc2_sids=[d2_1.sid, d2_2.sid],
        doc3_sids=[d3_1.sid, d3_2.sid]).create()
    d1_2 = Doc1(doc2_sids=[d2_1.sid], doc3_sids=[d3_1.sid]).create()

    d2_1.delete()
    d2_1.refresh().del_archived()
    d3_1.delete()
    d3_1.refresh().del_archived()

    d1_1 = d1_1.refresh()
    d1_2 = d1_2.refresh()

    assert d1_1.doc2_sids == [d2_2.sid]
    assert d1_1.doc3_sids == [d3_2.sid]

    assert d1_2.doc2_sids == []
    assert d1_2.doc3_sids == []

