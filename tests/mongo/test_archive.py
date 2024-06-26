from pykit.check import check
from pykit.err import NotFoundErr
from pykit.mark import MarkErr
from pykit.query import SearchQuery

from orwynn.mongo import Doc


class _ArchivableDoc(Doc):
    IS_ARCHIVABLE = True
    name: str
    price: float

class _NonArchivableDoc(Doc):
    IS_ARCHIVABLE = False
    name: str
    price: float

def test_get(app):
    # CREATING
    adoc1 = _ArchivableDoc(name="doc1", price=1.0).create()
    adoc2 = _ArchivableDoc(name="doc2", price=1.0).create()

    # ARCHIVING
    assert not adoc1.is_archived()
    adoc1 = adoc1.archive()
    assert adoc1.is_archived()

    docs = list(_ArchivableDoc.get_many())
    assert len(docs) == 1
    assert docs[0].name == adoc2.name

    docs = list(_ArchivableDoc.get_many(must_search_archived_too=True))
    assert len(docs) == 2

    # UNARCHIVING
    adoc1 = adoc1.refresh().unarchive()
    assert not adoc1.is_archived()

    docs = list(_ArchivableDoc.get_many())
    assert len(docs) == 2

def test_del(app):
    adoc = _ArchivableDoc(name="doc1", price=1.0).create()

    adoc.delete()
    adoc = adoc.refresh()
    check.expect(
        adoc.delete,
        MarkErr
    )
    adoc = _ArchivableDoc.get(
        SearchQuery.create_sid(adoc.sid),
        must_search_archived_too=True
    )
    assert adoc.is_archived()
    assert adoc.name == "doc1"

    # search without archive flag
    check.expect(
        _ArchivableDoc.get,
        NotFoundErr,
        { "sid": adoc.sid }
    )

    adoc.del_archived()
    check.expect(
        _ArchivableDoc.get,
        NotFoundErr,
        { "sid": adoc.sid }
    )
    check.expect(
        _ArchivableDoc.get,
        NotFoundErr,
        { "sid": adoc.sid },
        must_search_archived_too=True
    )

