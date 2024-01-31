from tests.mongo.conftest import SimpleDocument


def test_del(document_1: SimpleDocument, document_2: SimpleDocument):
    assert document_1.try_del()
    assert len(list(SimpleDocument.get_many())) == 1
