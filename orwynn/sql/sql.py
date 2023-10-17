from pathlib import Path
from typing import Optional, Sequence
from orwynn.utils import validation
from orwynn.base.database.database import Database

from .table import Table

from .enums import SQLDatabaseKind

from orwynn.sql.config import SQLConfig
from sqlalchemy import create_engine, Engine
from sqlalchemy import Table as SQLAlchemyTable
from sqlalchemy.orm import Session


class SQL(Database):
    def __init__(
        self,
        config: SQLConfig
    ) -> None:
        super().__init__()
        self.__config = config
        self.__engine: Engine = self._create_engine()

    @property
    def engine(self) -> Engine:
        return self.__engine

    @property
    def session(self) -> Session:
        """Returns a new session."""
        return Session(self.__engine)

    def create_tables(self, *tables: type[Table]) -> None:
        """Creates tables.

        Args:
            *tables:
                Tables to create. If no tables are given (or None), all
                reachable tables are created.
        """
        Table.metadata.create_all(
            self.__engine,
            tables=self._collect_sqla_tables(*tables)
        )

    def drop_tables(self, *tables: type[Table]) -> None:
        """Drops tables.

        Args:
            *tables:
                Tables to drop. If no tables are given (or None), all
                reachable tables are dropped.
        """
        Table.metadata.drop_all(
            self.__engine,
            tables=self._collect_sqla_tables(*tables)
        )

    def _collect_sqla_tables(
        self,
        *tables: type[Table]
    ) -> Optional[Sequence[SQLAlchemyTable]]:
        sqla_tables: Optional[Sequence[SQLAlchemyTable]] = None
        if tables:
            sqla_tables = []
            for table in tables:
                sqla_tables.append(table.__table__)  # type: ignore
        return sqla_tables

    def _create_engine(self) -> Engine:
        url: str
        connect_args: dict = {}
        final_kwargs: dict = {}

        match self.__config.database_kind:
            case SQLDatabaseKind.PostgreSQL:
                url = \
                    f"postgresql://{self.__config.database_user}" \
                    + f":{self.__config.database_password}" \
                    + f"@{self.__config.database_host}" \
                    + f":{self.__config.database_port}" \
                    + f"/{self.__config.database_name}"
            case SQLDatabaseKind.SQLite:
                database_path: str = validation.apply(
                    self.__config.database_path,
                    str
                )

                # Create directories for the path if they are not exist.
                # https://stackoverflow.com/a/273227/14748231
                Path(database_path).parent.mkdir(parents=True, exist_ok=True)

                # Note that here we add additional slash since in either
                # memory ":memory:", relative "var/app.db" or absolute
                # "/tmp/app.db" cases we have to prepend slash to comply with
                # SQLite standard.
                url = f"sqlite:///{database_path}"

                # Make SQLite know that more than one thread could interact
                # with the database for the same request.
                # See https://fastapi.tiangolo.com/tutorial/sql-databases/#note
                connect_args.update({"check_same_thread": False})
            case _:
                raise TypeError(
                    f"unknown database {self.__config.database_kind}"
                )

        final_kwargs["connect_args"] = connect_args
        final_kwargs["poolclass"] = self.__config.real_poolclass
        if self.__config.pool_size:
            final_kwargs["pool_size"] = self.__config.pool_size

        return create_engine(
            url,
            **final_kwargs
        )
