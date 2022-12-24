from pytest import fixture

from orwynn.app.App import App
from orwynn.boot.Boot import Boot


@fixture
def std_app(std_boot: Boot) -> App:
    return std_boot.app
