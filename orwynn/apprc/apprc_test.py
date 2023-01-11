import pytest

from orwynn import validation
from orwynn.apprc.AppRC import AppRC
from orwynn.boot.Boot import Boot
from orwynn.boot.BootMode import BootMode
from orwynn.config.Config import Config
from orwynn.di.DI import DI
from orwynn.model.Model import Model
from orwynn.module.Module import Module
from orwynn.mp import dictpp


class Menu(Model):
    __root__: dict[str, float]


class BurgerShotConfig(Config):
    location: str
    employees: int
    menu: Menu


@pytest.fixture
def raw_apprc() -> AppRC:
    return dictpp({
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
    })


def test_prod(raw_apprc: AppRC):
    Boot(
        root_module=Module("/", Providers=[BurgerShotConfig]),
        apprc=raw_apprc,
        mode=BootMode.PROD
    )

    assert validation.apply(
        DI.ie().find("BurgerShotConfig"),
        BurgerShotConfig
    ).dict() == raw_apprc["prod.BurgerShot"]


def test_dev(raw_apprc: AppRC):
    Boot(
        root_module=Module("/", Providers=[BurgerShotConfig]),
        apprc=raw_apprc,
        mode=BootMode.DEV
    )

    assert validation.apply(
        DI.ie().find("BurgerShotConfig"),
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


def test_test(raw_apprc: AppRC):
    Boot(
        root_module=Module("/", Providers=[BurgerShotConfig]),
        apprc=raw_apprc,
        mode=BootMode.TEST
    )

    assert validation.apply(
        DI.ie().find("BurgerShotConfig"),
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
