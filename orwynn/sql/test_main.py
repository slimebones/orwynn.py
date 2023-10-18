import contextlib
import os
from enum import Enum
from typing import Generator

import pytest
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from orwynn import sql
from orwynn.base.module import Module
from orwynn.boot import Boot
from orwynn.utils import validation
from orwynn.utils.crypto import hash_password

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
    await Boot.create(
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
