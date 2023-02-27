import pytest

from orwynn.util import validation
from orwynn.apprc._AppRc import AppRc
from orwynn.boot._Boot import Boot
from orwynn.boot._BootMode import BootMode
from orwynn.config.Config import Config
from orwynn.di.Di import Di
from orwynn.base.model.Model import Model
from orwynn.base.module.Module import Module
from orwynn.mp.helpers import find as mp_find


class Menu(Model):
    __root__: dict[str, float]


class BurgerShotConfig(Config):
    location: str
    employees: int
    menu: Menu


@pytest.fixture
def raw_apprc() -> AppRc:
    return {
        "prod": {
            "BurgerShot": {
                "location": "Vinewood",
                "employees": 15,
                "menu": {
                    "standard_burger": 1.25,
                    "cola": 1.5
                }
            }
        },
        "dev": {
            "BurgerShot": {
                "employees": 25,
                "menu": {
                    "cola": 1.8,
                    "pizza": 4.1,
                    "fried_chicken": 3.5
                }
            }
        },
        "test": {
            "BurgerShot": {
                "location": "Jefferson",
                "menu": {
                    "standard_burger": 1.1,
                    "fried_chicken": 5.0
                }
            }
        }
    }


def test_prod(raw_apprc: AppRc):
    Boot(
        root_module=Module("/", Providers=[BurgerShotConfig]),
        apprc=raw_apprc,
        mode=BootMode.PROD
    )

    assert validation.apply(
        Di.ie().find("BurgerShotConfig"),
        BurgerShotConfig
    ).dict() == mp_find("prod.BurgerShot", raw_apprc)


def test_dev(raw_apprc: AppRc):
    Boot(
        root_module=Module("/", Providers=[BurgerShotConfig]),
        apprc=raw_apprc,
        mode=BootMode.DEV
    )

    assert validation.apply(
        Di.ie().find("BurgerShotConfig"),
        BurgerShotConfig
    ).dict() == {
        "location": "Vinewood",
        "employees": 25,
        "menu": {
            "standard_burger": 1.25,
            "cola": 1.8,
            "pizza": 4.1,
            "fried_chicken": 3.5
        }
    }


def test_test(raw_apprc: AppRc):
    Boot(
        root_module=Module("/", Providers=[BurgerShotConfig]),
        apprc=raw_apprc,
        mode=BootMode.TEST
    )

    assert validation.apply(
        Di.ie().find("BurgerShotConfig"),
        BurgerShotConfig
    ).dict() == {
        "location": "Jefferson",
        "employees": 25,
        "menu": {
            "standard_burger": 1.1,
            "cola": 1.8,
            "pizza": 4.1,
            "fried_chicken": 5.0
        }
    }
