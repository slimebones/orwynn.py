from tests.mongo.conftest import NestedDocument, SimpleDocument


def test_main(document_1: SimpleDocument):
    f = document_1.try_upd({"$set": {"name": "beer"}})
    assert f
    assert f.name == "beer"

def test_two_fields(document_1: SimpleDocument):
    f = document_1.try_upd({
        "$set": {
            "name": "beer",
            "price": 2.5
        }
    })
    assert f
    assert f.name == "beer"
    assert f.price == 2.5

def test_nested(nested_document_1: NestedDocument):
    f = nested_document_1.try_set(
        {
            "nested.key1.key2": 2
        }
    )
    assert f
    assert f.nested["key1"]["key2"] == 2


def test_nested_unexistent(nested_document_1: NestedDocument):
    f = nested_document_1.try_set(
        {
            "nested.key1.key3": 4
        }
    )
    assert f
    assert f.nested["key1"]["key3"] == 4
