from typing import Optional, Sequence
from orwynn import Service, validation

from .Table import Table

from .SQLDatabase import SQLDatabase

from .SQLConfig import SQLConfig
from sqlalchemy import create_engine, Engine
from sqlalchemy import Table as SQLAlchemyTable
from sqlalchemy.orm import Session


class SQLService(Service):
    def __init__(
        self,
        config: SQLConfig
    ) -> None:
        super().__init__()
        self.__config = config
        self.__engine: Engine = self.__create_engine()

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
            tables=self.__collect_sqla_tables(*tables)
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
            tables=self.__collect_sqla_tables(*tables)
        )

    def __collect_sqla_tables(
        self,
        *tables: type[Table]
    ) -> Optional[Sequence[SQLAlchemyTable]]:
        sqla_tables: Optional[Sequence[SQLAlchemyTable]] = None
        if tables:
            sqla_tables = []
            for table in tables:
                sqla_tables.append(table.__table__)  # type: ignore
        return sqla_tables

    def __create_engine(self) -> Engine:
        url: str
        connect_args: dict = {}
        match self.__config.database_type:
            case SQLDatabase.POSTGRESQL:
                url = \
                    f"postgresql://{self.__config.database_user}" \
                    + f"{self.__config.database_password}" \
                    + f"@{self.__config.database_host}" \
                    + f":{self.__config.database_port}" \
                    + f"/{self.__config.database_name}"
            case SQLDatabase.SQLITE:
                database_path: str = validation.apply(
                    self.__config.database_path,
                    str
                )
                # Correct in-memory url to avoid url building problems
                if database_path == ":memory:":
                    database_path = "/:memory:"

                url = f"sqlite://{database_path}"

                # Make SQLite know that more than one thread could interact
                # with the database for the same request.
                # See https://fastapi.tiangolo.com/tutorial/sql-databases/#note
                connect_args.update({"check_same_thread": False})
            case _:
                raise TypeError(
                    f"unknown database {self.__config.database_type}"
                )
        return create_engine(
            url, connect_args=connect_args
        )
