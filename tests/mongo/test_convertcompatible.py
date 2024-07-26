from enum import Enum

from pykit.check import check

from orwynn.mongo import Mongo


class StringEnum(Enum):
    Red = "red"
    Green = "green"


class StringObj:
    @property
    def mongovalue(self) -> str:
        return "hello"


class DictObj:
    @property
    def mongovalue(self) -> dict:
        return {
            1: "hello",
            2: "world",
        }


class SetObj:
    @property
    def mongovalue(self) -> set:
        return {1, 2, 3}


def test_already_compatible():
    """
    Should work correctly for already compatible types.
    """
    assert Mongo.convert_compatible("hello") == "hello"
    assert Mongo.convert_compatible(2) == 2
    assert Mongo.convert_compatible(2.3) == 2.3
    assert Mongo.convert_compatible(True) is True
    assert Mongo.convert_compatible([1, 2, 3]) == [1, 2, 3]
    assert Mongo.convert_compatible({
        1: "hello",
        2: "world",
    }) == {
        1: "hello",
        2: "world",
    }
    assert Mongo.convert_compatible(None) is None


def test_containers():
    """
    Should work correctly for containers, like list or dict, which also may
    contain sub-containers.
    """
    mock_dict: dict = {
        1: {
            1: "hello",
            2: "world",
        },
        2: [
            {
                1: "hello",
                2: "world",
            },
            {
                1: "here",
                2: "we",
                3: "go",
                4: ["again", "!!"],
            },
        ],
    }

    assert Mongo.convert_compatible(mock_dict) == mock_dict


def test_enum_string():
    """
    Should convert enum correctly.
    """
    assert Mongo.convert_compatible(StringEnum.Red) == "red"


def test_mongovalue_string():
    """
    Should convert objects with attribute `mongovalue`.
    """
    assert Mongo.convert_compatible(StringObj()) == "hello"


def test_mongovalue_dict():
    """
    Should convert objects with attribute `mongovalue` which returns
    dict.
    """
    assert Mongo.convert_compatible(DictObj()) == {
        1: "hello",
        2: "world",
    }


def test_mongovalue_set():
    """
    Should raise an error for set returning mongovalue attribute.
    """
    check.expect(
        Mongo.convert_compatible,
        ValueError,
        SetObj(),
    )
