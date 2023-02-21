from orwynn.mp.dictpp import dictpp
from orwynn.mp.helpers import patch


def test_patch():
    a = dictpp({
        "BurgerShot": {
            "location": "Vinewood",
            "employees": 15,
            "menu": {
                "standard_burger": 1.25,
                "big_burger": 2.3,
                "cola": 1.5
            }
        }
    })
    b = dictpp({
        "BurgerShot": {
            "menu": {
                "cola": 1.8,
                "pizza": 4.1,
                "donut": 1.3
            }
        }
    })

    result = patch(a, b)

    assert result == {
        "BurgerShot": {
            "location": "Vinewood",
            "employees": 15,
            "menu": {
                "standard_burger": 1.25,
                "big_burger": 2.3,
                "cola": 1.8,
                "pizza": 4.1,
                "donut": 1.3
            }
        }
    }


def test_patch_no_deepcopy():
    a = dictpp({
        "BurgerShot": {
            "location": "Vinewood",
            "employees": 15,
            "menu": {
                "standard_burger": 1.25,
                "big_burger": 2.3,
                "cola": 1.5
            }
        }
    })
    b = dictpp({
        "BurgerShot": {
            "menu": {
                "cola": 1.8,
                "pizza": 4.1,
                "donut": 1.3
            }
        }
    })

    patch(a, b, should_deepcopy=False)

    assert a == {
        "BurgerShot": {
            "location": "Vinewood",
            "employees": 15,
            "menu": {
                "standard_burger": 1.25,
                "big_burger": 2.3,
                "cola": 1.8,
                "pizza": 4.1,
                "donut": 1.3
            }
        }
    }
