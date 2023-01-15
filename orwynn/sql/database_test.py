from pytest import fixture
from staze.core.app.app import App

from staze.core.database.database import Database
from staze.core.log.log import log


@fixture
def db(self, app: App):
    database: Database = Database.instance()

    with app.app_context():
        database.drop_all()
        database.create_all()

    yield database

    with app.app_context():
        database.drop_all()
