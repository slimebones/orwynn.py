from pytest import fixture

from orwynn.base.database.DatabaseKind import DatabaseKind
from orwynn.base.module import Module
from orwynn.boot.Boot import Boot
from orwynn.mongo import Document


class Item(Document):
    name: str
    price: float


@fixture
def run_mongo_boot():
    Boot(Module(route="/"), databases=[DatabaseKind.MONGO])


@fixture
def create_item(run_mongo_boot) -> Item:
    return Item(name="pizza", price=1.2).create()


@fixture
def create_two_items(run_mongo_boot) -> list[Item]:
    items: list[Item] = []
    items.append(Item(name="pizza", price=1.2).create())
    items.append(Item(name="donut", price=1).create())
    return items


def test_create(run_mongo_boot):
    created = Item(name="pizza", price=1.2).create()

    assert created.name == "pizza"
    assert created.price == 1.2


def test_find_all(create_two_items: list[Item]):
    assert list(Item.find_all()) == create_two_items


def test_find_one(create_item: Item):
    assert Item.find_one(id=create_item.id) == create_item


def test_remove(create_two_items: list[Item]):
    assert create_two_items[0].remove() == create_two_items[0]
    assert len(list(Item.find_all())) == 1


def test_update(create_item: Item):
    assert create_item.update(set={"name": "beer"}).name == "beer"


def test_update_two_fields(create_item: Item):
    item: Item = create_item.update(set={"name": "beer", "price": 2.5})
    assert item.name == "beer"
    assert item.price == 2.5
