from pytest import fixture
from orwynn.src.app.app_service import AppService

from orwynn.src.boot.boot import Boot


@fixture
def boot() -> Boot:
    return Boot()

@fixture
def app(boot: Boot) -> AppService:
    return boot.app