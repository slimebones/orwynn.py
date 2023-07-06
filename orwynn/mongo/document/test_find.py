
from orwynn.mongo.document.testing import SimpleDocument


def test_one(document_1: SimpleDocument, document_2: SimpleDocument):
    assert SimpleDocument.find_one({"id": document_1.id}) == document_1


def test_all(document_1: SimpleDocument, document_2: SimpleDocument):
    assert {item.id for item in SimpleDocument.find_all()} == {document_1.id,
        document_2.id}


def test_all_limited(document_1: SimpleDocument, document_2: SimpleDocument):
    assert len(list(SimpleDocument.find_all(limit=1))) == 1


def test_all_id_operators(
    document_1: SimpleDocument,
    document_2: SimpleDocument
):
    """
    Should work normally for id MongoDb operators.
    """
    found: list[SimpleDocument] = list(SimpleDocument.find_all({
        "id": {
            "$in": [
                document_1.id
            ]
        }
    }))

    assert len(found) == 1
    assert found[0].id == document_1.id
