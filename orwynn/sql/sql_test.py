from enum import Enum
from typing import Generator
from orwynn import Boot, Module
import pytest

from .EnumField import EnumField

from .Table import Table

from ..sensor.SensorMeasurement import SensorMeasurement

from .SQLDatabase import SQLDatabase

from .SQLConfig import SQLConfig

from .SQLService import SQLService

@fixture
def db(self, app: App):
    database: Database = Database.instance()

    with app.app_context():
        database.drop_all()
        database.create_all()

    yield database

    with app.app_context():
        database.drop_all()

@pytest.fixture
def sqlite() -> SQLService:
    return SQLService(SQLConfig(
        database_type=SQLDatabase.SQLITE,
        database_name=":memory:"
    ))


def test_sqlite_init():
    sv = SQLService(SQLConfig(
        database_type=SQLDatabase.SQLITE,
        database_name=":memory:"
    ))
    sv.create_tables()
    sv.drop_tables()


def test_postgresql_init():
    sv = SQLService(SQLConfig(
        database_type=SQLDatabase.POSTGRESQL,
        database_name="hqb-test",
        database_user="postgres",
        database_password="postgres",
        database_host="localhost",
        database_port=5432
    ))
    sv.create_tables()
    sv.drop_tables()


def test_enum_field(sqlite: SQLService):
    Color = Enum("Color", ["RED", "BLUE", "GREEN"])

    class T1(Table):
        color = EnumField(Color)

    sqlite.drop_tables(T1)
    sqlite.create_tables(T1)

    T1.create(color=Color.RED)
    assert T1.get_by_id(1).color == Color.RED

    T1.create(color=Color.GREEN)
    assert T1.get_by_id(2).color == Color.GREEN

    T1.create(color=Color.BLUE)
    assert T1.get_by_id(3).color == Color.BLUE
