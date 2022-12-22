from pytest import fixture

from orwynn.app._AppService import AppService
from orwynn.boot._Boot import Boot


@fixture
def std_app(std_boot: Boot) -> AppService:
    return std_boot.app
