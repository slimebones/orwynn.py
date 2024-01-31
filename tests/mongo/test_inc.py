from tests.mongo.conftest import NestedDocument, SimpleDocument


def test_main(document_1: SimpleDocument):
    f = document_1.try_upd({"$inc": {"price": 2.5}})
    assert f
    assert f.price == 3.7


def test_nested(nested_document_1: NestedDocument):
    f = nested_document_1.try_upd(
        {
            "$inc": {
                "nested.key1.key2": 2
            }
        }
    )
    assert f
    assert f.nested["key1"]["key2"] == 3


def test_nested_unexistent(nested_document_1: NestedDocument):
    f = nested_document_1.try_upd(
        {
            "$inc": {
                "nested.key1.key3": 3
            }
        }
    )
    assert f
    assert f.nested["key1"]["key3"] == 3
