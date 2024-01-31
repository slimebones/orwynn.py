from tests.mongo.conftest import SimpleDocument


def test_main(
    document_1: SimpleDocument
):
    document_1.try_upd({
        "$set": {
            "price": 5.0
        }
    })

    assert document_1.price == 1.2
    document_1 = document_1.refresh()
    assert document_1.price == 5.0
