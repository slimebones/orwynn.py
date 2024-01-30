from orwynn.mongo.document.testing import SimpleDocument


def test_main(document_1: SimpleDocument, document_2: SimpleDocument):
    assert {item.id for item in SimpleDocument.get()} == {document_1.id,
        document_2.id}


def test_limited(document_1: SimpleDocument, document_2: SimpleDocument):
    assert len(list(SimpleDocument.get(limit=1))) == 1


def test_id_operators(
    document_1: SimpleDocument,
    document_2: SimpleDocument
):
    """
    Should work normally for id MongoDb operators.
    """
    found: list[SimpleDocument] = list(SimpleDocument.get({
        "id": {
            "$in": [
                document_1.id
            ]
        }
    }))

    assert len(found) == 1
    assert found[0].id == document_1.id
