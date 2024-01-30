from orwynn.mongo.document.testing import NestedDocument, SimpleDocument


def test_main(document_1: SimpleDocument):
    item: SimpleDocument = document_1.update(inc={"price": 2.5})
    assert item.price == 3.7


def test_nested(nested_document_1: NestedDocument):
    new: NestedDocument = nested_document_1.update(
        inc={
            "nested.key1.key2": 2
        }
    )

    assert new.nested["key1"]["key2"] == 3


def test_nested_unexistent(nested_document_1: NestedDocument):
    new: NestedDocument = nested_document_1.update(
        # incremention works as set on empty fields
        inc={
            "nested.key1.key3": 3
        }
    )

    assert new.nested["key1"]["key3"] == 3
