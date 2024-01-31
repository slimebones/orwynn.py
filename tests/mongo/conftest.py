import pytest

from orwynn.mongo import Doc


class SimpleDocument(Doc):
    name: str
    price: float
    priority: int = 5


class NestedDocument(Doc):
    nested: dict


@pytest.fixture
def document_1() -> SimpleDocument:
    return SimpleDocument(
        name="pizza",
        price=1.2,
        priority=2
    ).create()


@pytest.fixture
def document_2() -> SimpleDocument:
    return SimpleDocument(
        name="donut",
        price=1
    ).create()


@pytest.fixture
def nested_document_1() -> NestedDocument:
    return NestedDocument(
        nested={
            "key1": {
                "key2": 1
            }
        }
    ).create()
