import os
from pathlib import Path
from typing import Optional, Sequence

from pykit import validation
from pykit.errors import UnsupportedError
from pykit.env import EnvUtils
from pykit.errors import PleaseDefineError, StrExpectError
from sqlalchemy import Engine
from sqlalchemy import Table as SQLAlchemyTable
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from orwynn.app.mode import AppMode
from orwynn.database.database import Database
from orwynn.log.log import Log
from orwynn.proxy.boot import BootProxy
from orwynn.sql.config import SQLConfig
from orwynn.sql.constants import (PSQLStatementConstants)

from .enums import SQLDatabaseKind
from .table import Table


class SQL(Database):
    def __init__(
        self,
        config: SQLConfig
    ) -> None:
        super().__init__()
        self._config = config
        self._engine: Engine = self._create_engine()

    @property
    def engine(self) -> Engine:
        return self._engine

    @property
    def should_drop_sql(self) -> bool:
        if (self._config.should_drop_env_spec is None):
            raise PleaseDefineError(
                cannot_do="should drop sql environ retrieval",
                please_define="SQLConfig.should_drop_sql_env_spec"
            )

        return EnvUtils.get_bool(self._config.should_drop_env_spec)

    @property
    def session(self) -> Session:
        """Returns a new session."""
        return Session(self._engine)

    def create_tables(self, *tables: type[Table]) -> None:
        """Creates tables.

        Args:
            *tables:
                Tables to create. If no tables are given (or None), all
                reachable tables are created.
        """
        Table.metadata.create_all(
            self._engine,
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
            self._engine,
            tables=self._collect_sqla_tables(*tables)
        )

    def recreate_public_schema_cascade(
        self
    ) -> None:
        if (self._config.database_kind is SQLDatabaseKind.SQLite):
            raise UnsupportedError(
                value="sqlite database for cascade recreating"
            )

        if (
            # lock drop in prod mode for error-protection
            BootProxy.ie().mode != AppMode.PROD
        ):
            Log.info("recreating sql database (public cascade)")
            # use raw sql since i haven't found a quick way to drop cascade
            # using python objects
            statement: str = (
                PSQLStatementConstants.RecreatePublicSchemaCascade
            )

            with self.session as s:
                s.execute(text(statement))
                s.commit()

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

        match self._config.database_kind:
            case SQLDatabaseKind.PostgreSQL:
                url = \
                    f"postgresql://{self._config.database_user}" \
                    + f":{self._config.database_password}" \
                    + f"@{self._config.database_host}" \
                    + f":{self._config.database_port}" \
                    + f"/{self._config.database_name}"
            case SQLDatabaseKind.SQLite:
                database_path: str = validation.apply(
                    self._config.database_path,
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
                    f"unknown database {self._config.database_kind}"
                )

        final_kwargs["connect_args"] = connect_args
        final_kwargs["poolclass"] = self._config.real_poolclass
        if self._config.pool_size:
            final_kwargs["pool_size"] = self._config.pool_size

        return create_engine(
            url,
            **final_kwargs
        )
