from pytest import fixture

from orwynn import validation
from orwynn.src.boot.Boot import Boot
from orwynn.src.module.Module import Module
from orwynn.src.mongo import module
from orwynn.src.mongo.Document import Document
from orwynn.src.mongo.DocumentUpdateError import DocumentUpdateError


class Item(Document):
    name: str
    price: float
    priority: int = 5


@fixture
def run_mongo_boot():
    Boot(
        Module(route="/", imports=[module.module]),
        apprc={
            "prod": {
                "Mongo": {
                    "database_name": "orwynn-test"
                }
            }
        }
    )


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
    assert Item.find_one({"id": create_item.id}) == create_item


def test_remove(create_two_items: list[Item]):
    assert create_two_items[0].remove() == create_two_items[0]
    assert len(list(Item.find_all())) == 1


def test_set(create_item: Item):
    assert create_item.update(set={"name": "beer"}).name == "beer"


def test_set_two_fields(create_item: Item):
    item: Item = create_item.update(set={"name": "beer", "price": 2.5})
    assert item.name == "beer"
    assert item.price == 2.5


def test_inc(create_item: Item):
    item: Item = create_item.update(inc={"price": 2.5})
    assert item.price == 3.7


def test_set_wrong_type(create_item: Item):
    validation.expect(
        create_item.update,
        DocumentUpdateError,
        set={"price": "sold out"}
    )


def test_inc_wrong_type(create_item: Item):
    validation.expect(
        create_item.update,
        DocumentUpdateError,
        inc={"priority": 5.5}
    )


def test_set_unexistent(create_item: Item):
    validation.expect(
        create_item.update,
        DocumentUpdateError,
        set={"wow": "post malone"}
    )


def test_inc_unexistent(create_item: Item):
    validation.expect(
        create_item.update,
        DocumentUpdateError,
        inc={"wow": "post malone"}
    )


def test_find_all_limited(create_two_items):
    assert len(list(Item.find_all(limit=1))) == 1


# FIXME: Temporarily transactions are not supported due to requirement of
#   installing replica set, which i don't want to adapt right now,
#   see https://www.mongodb.com/community/forums/t/why-replica-set-is-mandatory-for-transactions-in-mongodb/9533  # noqa: E501
# def test_success_transaction(create_item: Item):
#     def __create_item(s):

#     with Item.start_session() as session:


# def test_failed_transaction(create_item: Item):
#     def __create_item(s: ClientSession):

#     with Item.start_session() as session:
#         validation.expect(
#             session.with_transaction,
#             DocumentUpdateError,
#             __create_item

#     # Original name should be unchanged, new item not created
