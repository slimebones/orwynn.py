from orwynn.mongo import Doc


class _ArchivableDoc1(Doc):
    IsArchivable = True
    name: str
    price: float

class _NonArchivableDoc1(Doc):
    IsArchivable = False
    name: str
    price: float

def test_get(app):
    # CREATING
    adoc1 = _ArchivableDoc1(name="doc1", price=1.0).create()
    adoc2 = _ArchivableDoc1(name="doc2", price=1.0).create()

    # ARCHIVING
    assert not adoc1.is_archived()
    adoc1 = adoc1.archive()
    assert adoc1.is_archived()

    docs = list(_ArchivableDoc1.get_many())
    assert len(docs) == 1
    assert docs[0].name == adoc2.name

    docs = list(_ArchivableDoc1.get_many(must_search_archived_too=True))
    assert len(docs) == 2

    # UNARCHIVING
    adoc1 = adoc1.refresh().unarchive()
    assert not adoc1.is_archived()

    docs = list(_ArchivableDoc1.get_many())
    assert len(docs) == 2

