from pytest import fixture
from orwynn.app.app_service import AppService

from orwynn.boot.boot import Boot


@fixture
def boot() -> Boot:
    return Boot()

@fixture
def app(boot: Boot) -> AppService:
    return boot.app