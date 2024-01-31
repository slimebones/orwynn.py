from typing import Any

from orwynn.mongo import MongoUtils


def test_s1():
    result: dict[str, Any] = MongoUtils.convert_dict({
        "a1": {
            "a2": "b1",
            "a3": "b2",
        },
    })

    assert result == {
        "a1.a2": "b1",
        "a1.a3": "b2",
    }


def test_s2():
    result: dict[str, Any] = MongoUtils.convert_dict({
        "a1": {
            "a2": {
                "a3": 10,
                "a4": 20,
            },
            "a5": "b1",
            "a6": "b2",
        },
    })

    assert result == {
        "a1.a2.a3": 10,
        "a1.a2.a4": 20,
        "a1.a5": "b1",
        "a1.a6": "b2",
    }


def test_s3():
    result: dict[str, Any] = MongoUtils.convert_dict({
        "a1": {
            "a2": {
                "$in": [1, 2, 3],
            },
            "a3": {
                "$exists": True,
            },
            "a4": {
                "$somevalue": {
                    "notconverted": 1,
                },
            },
            "a5": {
                "somevalue": {
                    "converted": 10,
                },
            },
        },
    })

    assert result == {
        "a1.a2": {
            "$in": [1, 2, 3],
        },
        "a1.a3": {
            "$exists": True,
        },
        "a1.a4": {
            "$somevalue": {
                "notconverted": 1,
            },
        },
        "a1.a5.somevalue.converted": 10,
    }
