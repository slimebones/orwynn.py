import pytest

from orwynn.mongo.document import Document


class SimpleDocument(Document):
    name: str
    price: float
    priority: int = 5


class NestedDocument(Document):
    nested: dict


@pytest.fixture
def document_1(mongo_boot) -> SimpleDocument:
    return SimpleDocument(
        name="pizza",
        price=1.2,
        priority=2
    ).create()


@pytest.fixture
def document_2(mongo_boot) -> SimpleDocument:
    return SimpleDocument(
        name="donut",
        price=1
    ).create()


@pytest.fixture
def nested_document_1(mongo_boot) -> NestedDocument:
    return NestedDocument(
        nested={
            "key1": {
                "key2": 1
            }
        }
    ).create()
