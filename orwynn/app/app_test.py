from pytest import fixture

from orwynn.app import AppService
from orwynn.boot import Boot


@fixture
def std_app(std_boot: Boot) -> AppService:
    return std_boot.app
