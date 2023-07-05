from bson import ObjectId

from orwynn.mongo.document.errors import InvalidIdError
from orwynn.mongo.document.helpers import convert_to_object_id
from orwynn.utils import validation


def test_str():
    object_id: ObjectId = ObjectId()

    result: str | ObjectId = convert_to_object_id(str(object_id))

    assert type(result) is ObjectId
    assert result == object_id


def test_object_id():
    object_id: ObjectId = ObjectId()

    result: ObjectId = convert_to_object_id(object_id)

    assert type(result) is ObjectId
    assert result == object_id


def test_int():
    result: int | ObjectId = convert_to_object_id(1)

    assert type(result) is int
    assert result == 1


def test_dict():
    object_id: ObjectId = ObjectId()

    result: dict | ObjectId = convert_to_object_id({
        "hello": str(object_id)
    })

    assert type(result) is dict
    assert result["hello"] == object_id


def test_list():
    object_id_1: ObjectId = ObjectId()
    object_id_2: ObjectId = ObjectId()

    result: list | ObjectId = convert_to_object_id([
        str(object_id_1), str(object_id_2)
    ])

    assert type(result) is list
    assert len(result) == 2
    assert {str(x) for x in result} == {str(object_id_1), str(object_id_2)}


def test_invalid_id():
    validation.expect(
        convert_to_object_id,
        InvalidIdError,
        "hello"
    )
