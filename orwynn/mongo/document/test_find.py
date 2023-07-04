from pytest import fixture

from orwynn import mongo
from orwynn.base.module import Module
from orwynn.boot.boot import Boot
from orwynn.mongo.testing import Item
from orwynn.utils import validation

from . import Document
from ..errors import DocumentUpdateError


def test_one(document_1: Item, document_2: Item):
    assert Item.find_one({"id": document_1.id}) == document_1


def test_all(document_1: Item, document_2: Item):
    assert set(item.id for item in Item.find_all()) == set([
        document_1.id,
        document_2.id
    ])


def test_all_limited(document_1: Item, document_2: Item):
    assert len(list(Item.find_all(limit=1))) == 1


def test_all_id_operators(
    document_1: Item,
    document_2: Item
):
    """
    Should work normally for id MongoDb operators.
    """
    found: list[Item] = list(Item.find_all({
        "id": {
            "$in": [
                document_1.id
            ]
        }
    }))

    assert len(found) == 1
    assert found[0].id == document_1.id
