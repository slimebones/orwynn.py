from orwynn.mp import patch, dictpp


def test_patch():
    a = dictpp({
        "BurgetShot": {
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
        "BurgetShot": {
            "menu": {
                "cola": 1.8,
                "pizza": 4.1,
                "donut": 1.3
            }
        }
    })

    result = patch(a, b)

    assert result == {
        "BurgetShot": {
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
        "BurgetShot": {
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
        "BurgetShot": {
            "menu": {
                "cola": 1.8,
                "pizza": 4.1,
                "donut": 1.3
            }
        }
    })

    patch(a, b, should_deepcopy=False)

    assert a == {
        "BurgetShot": {
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
