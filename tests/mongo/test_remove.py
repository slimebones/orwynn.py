from orwynn.mongo.document.testing import SimpleDocument


def test_remove(document_1: SimpleDocument, document_2: SimpleDocument):
    assert document_1.remove() == document_1
    assert len(list(SimpleDocument.find_all())) == 1
