import contextlib
import os
from enum import Enum
from typing import Generator

import pytest
from pykit import validation
from pykit.crypto import hash_password
from sqlalchemy import ForeignKey
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped, mapped_column, relationship

from orwynn import sql
from orwynn import App
from orwynn.di.di import Di
from orwynn.module import Module
from orwynn.sql import module as sql_module
from orwynn.sql.shd import SHD

from .config import SQLConfig
from .enums import SQLDatabaseKind
from .sql import SQL
from .table import Table


class User(Table):
    name: Mapped[str]
    hpassword: Mapped[str]
    tweets: Mapped[list["Tweet"]] = relationship(backref="user")
    likes: Mapped[list["Like"]] = relationship(backref="user")


class Tweet(Table):
    title: Mapped[str]
    text: Mapped[str]
    likes: Mapped[list["Like"]] = relationship(backref="tweet")
    user_id: Mapped[int] = mapped_column(ForeignKey("user._id"), nullable=True)


class Like(Table):
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user._id"),
        nullable=True
    )
    tweet_id: Mapped[int] = mapped_column(
        ForeignKey("tweet._id"),
        nullable=True
    )


@pytest.fixture
def _sqlite() -> Generator:
    service = SQL(SQLConfig(
        database_kind=SQLDatabaseKind.SQLite,
        database_path=":memory:"
    ))

    service.create_tables()

    yield service

    service.drop_tables()


@pytest.fixture
def _user1() -> User:
    return User(
        name="Tommy",
        hpassword=hash_password("vicecity"),
    )


@pytest.fixture
def _user2() -> User:
    return User(
        name="Lance",
        hpassword=hash_password("vancenotdance")
    )


@pytest.fixture
def _tweet1() -> Tweet:
    return Tweet(
        title="Ice Cream Factory",
        text="Make 50 sells!"
    )


@pytest.fixture
def _like1() -> Like:
    return Like()


@pytest.fixture
def _add_user1(_sqlite: SQL, _user1: User) -> None:
    with _sqlite.session as session:
        session.add(_user1)
        session.commit()


@pytest.fixture
def _add_user2(_sqlite: SQL, _user2: User) -> None:
    with _sqlite.session as session:
        session.add(_user2)
        session.commit()


@pytest.fixture
def _add_tweet1(_sqlite: SQL, _tweet1: Tweet) -> None:
    with _sqlite.session as session:
        session.add(_tweet1)
        session.commit()


@pytest.fixture
def _add_like1(_sqlite: SQL, _like1: Like) -> None:
    with _sqlite.session as session:
        session.add(_like1)
        session.commit()


@pytest.fixture
def _connect_user1a2_tweet1_like1(
    _sqlite: SQL,
    _add_user1,
    _add_user2,
    _add_tweet1,
    _add_like1
) -> None:
    with _sqlite.session as s:
        user1: User = validation.check(s.get(User, 1))
        user2: User = validation.check(s.get(User, 2))
        tweet1: Tweet = validation.check(s.get(Tweet, 1))
        like1: Like = validation.check(s.get(Like, 1))
        user2.likes.append(like1)
        tweet1.likes.append(like1)
        user1.tweets.append(tweet1)
        s.commit()


def test_sqlite_init_memory():
    sql = SQL(SQLConfig(
        database_kind="sqlite",
        database_path=":memory:"
    ))
    sql.create_tables()
    sql.drop_tables()


@pytest.mark.asyncio
async def test_recreate_cascade_with_environ(
    setenv_orwynntest_should_drop_sql_to_1
):
    class Item(Table):
        price: Mapped[float]

        @declared_attr.directive
        def __tablename__(cls) -> str:
            return "recreate_cascade_with_environ_item"

    await App.create(
        Module(
            imports=[sql_module]
        ),
        apprc={
            "prod": {
                "SQL": {
                    "database_kind": "postgresql",
                    "database_name": "orwynn_test",
                    "database_user": "postgres",
                    "database_password": "postgres",
                    "database_host": "localhost",
                    "database_port": 9005,
                    "should_drop_env_spec": {
                        "key": "ORWYNNTEST_SHOULD_DROP_SQL"
                    }
                }
            }
        }
    )
    sql: SQL = Di.ie().find("SQL")

    sql.drop_tables()
    sql.create_tables()
    try:
        with SHD.new(sql) as shd:
            item = Item(price=10.2)
            shd.add(item)
            item = Item(price=15.5)
            shd.add(item)
            shd.commit()
            assert len(shd.scalars(shd.select(Item)).all()) == 2
        assert sql.should_drop_sql
        sql.recreate_public_schema_cascade()
        validation.expect(
            shd.scalars,
            ProgrammingError,
            shd.select(Item)
        )
    finally:
        sql.drop_tables()


def test_sqlite_default():
    """
    Default config should be sqlite memory db.
    """
    sql = SQL(SQLConfig())
    sql.create_tables()
    sql.drop_tables()


def test_sqlite_init_relative_path():
    # Delete old data to ensure auto directory creating is working.
    with contextlib.suppress(FileNotFoundError):
        try:
            os.removedirs(os.path.join(
                os.getcwd(), "var/tmp"
            ))
        except OSError: # Directory not empty
            os.remove(os.path.join(
                os.getcwd(), "var/tmp/test.db"
            ))

    sql = SQL(SQLConfig(
        database_kind="sqlite",
        database_path="var/tmp/test.db"
    ))
    sql.create_tables()
    sql.drop_tables()


def test_sqlite_init_absolute_path():
    # Delete old data to ensure auto directory creating is working.
    with contextlib.suppress(FileNotFoundError):
        try:
            os.removedirs("/tmp/orwynn")  # noqa: S108
        except OSError: # Directory not empty
            os.remove("/tmp/orwynn/test.db")  # noqa: S108

    sql = SQL(SQLConfig(
        database_kind="sqlite",
        database_path="/tmp/orwynn/test.db"  # noqa: S108
    ))
    sql.create_tables()
    sql.drop_tables()


def test_postgresql_init():
    sql = SQL(SQLConfig(
        database_kind="postgresql",
        database_name="orwynn_test",
        database_user="postgres",
        database_password="postgres",  # noqa: S106
        database_host="localhost",
        database_port=9005
    ))
    sql.create_tables()
    sql.drop_tables()


def test_create(
    _sqlite: SQL,
    _connect_user1a2_tweet1_like1
):
    with _sqlite.session as s:
        user2: User = validation.check(s.get(User, 2))
        tweet1: Tweet = validation.check(s.get(Tweet, 1))
        like1: Like = validation.check(s.get(Like, 1))

        assert validation.check(s.get(User, 1)).tweets == [tweet1]
        assert tweet1.likes == [like1]
        assert user2.likes == [like1]


def test_enum_field(_sqlite: SQL):
    class Color(Enum):
        RED = 1
        BLUE = 2
        GREEN = 3

    class Item(Table):
        color: Mapped[Color]

    _sqlite.create_tables(Item)
    with _sqlite.session as s:
        s.add(Item(color=Color.RED))
        s.add(Item(color=Color.BLUE))
        s.add(Item(color=Color.GREEN))
        s.commit()

        assert validation.check(s.get(Item, 1)).color == Color.RED
        assert validation.check(s.get(Item, 2)).color == Color.BLUE
        assert validation.check(s.get(Item, 3)).color == Color.GREEN


@pytest.mark.asyncio
async def test_config_poolclass():
    await App.create(
        Module(imports=[sql.module]),
        apprc={
            "prod": {
                "SQL": {
                    "database_kind": "sqlite",
                    "database_path": ":memory:",
                    "poolclass": "StaticPool"
                }
            }
        }
    )
