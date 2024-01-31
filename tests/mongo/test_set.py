from orwynn.mongo.document.testing import NestedDocument, SimpleDocument


def test_main(document_1: SimpleDocument):
    assert document_1.update(set={"name": "beer"}).name == "beer"


def test_two_fields(document_1: SimpleDocument):
    item: SimpleDocument = document_1.update(
        set={"name": "beer", "price": 2.5}
    )
    assert item.name == "beer"
    assert item.price == 2.5


def test_nested(nested_document_1: NestedDocument):
    new: NestedDocument = nested_document_1.update(
        set={
            "nested.key1.key2": 2
        }
    )

    assert new.nested["key1"]["key2"] == 2


def test_nested_unexistent(nested_document_1: NestedDocument):
    new: NestedDocument = nested_document_1.update(
        set={
            "nested.key1.key3": 4
        }
    )

    assert new.nested["key1"]["key3"] == 4
