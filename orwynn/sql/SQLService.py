from orwynn import Service, validation

from .Table import Table

from .SQLDatabase import SQLDatabase

from .SQLConfig import SQLConfig
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base


class SQLService(Service):
    def __init__(
        self,
        config: SQLConfig
    ) -> None:
        super().__init__()
        self.__config = config

        SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
        # SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

        engine = create_engine(
            SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
        )

    # def connect(self) -> None:
    #     self.__database.connect()

    # def close(self) -> None:
    #     self.__database.close()

    def create_tables(
        self,
        *tables: type[Table]
    ) -> None:
        """Creates tables in database.

        If "tables" not given, creates all reachable tables in subclass system.
        Otherwise init only tables given.
        """
        if tables:
            validation.validate_each(
                tables, Table, expected_sequence_type=tuple
            )
            self.__database.create_tables(tables)
        else:
            self.__database.create_tables(self.__Tables)

    def drop_tables(
        self,
        *tables: type[Table]
    ) -> None:
        """Drops tables in database.

        If "tables" not given, drops all reachable tables in subclass system.
        Otherwise drop only tables given.
        """
        if tables:
            validation.validate_each(
                tables, Table, expected_sequence_type=tuple
            )
            self.__database.drop_tables(tables)
        else:
            self.__database.drop_tables(self.__Tables)

    def __init(self) -> Database:
        match self.__config.database_type:
            case SQLDatabase.POSTGRESQL:
                return PostgresqlDatabase(
                    self.__config.database_name,
                    user=self.__config.database_user,
                    password=self.__config.database_password,
                    host=self.__config.database_host,
                    port=self.__config.database_port
                )
            case SQLDatabase.SQLITE:
                return SqliteDatabase(
                    self.__config.database_name
                )
            case _:
                raise TypeError(
                    f"unknown database {self.__config.database_type}"
                )

from __future__ import annotations
import re
from functools import wraps
from typing import TYPE_CHECKING, Callable, Any, TypeVar

from warepy import format_message, snakefy
from staze.core.database.orm_not_found_error import OrmNotFoundError
from staze.core.model.model import Model
from staze.core.log.log import log
from flask import Flask
import flask_migrate
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy import Model as BaseOrm
import sqlalchemy as sa

from staze.core.service.service import Service
from .database_type_enum import DatabaseTypeEnum

if TYPE_CHECKING:
    hybrid_property = property


AnyOrm = TypeVar('AnyOrm', bound='Database.Orm')


# TODO: Fix type hinting for decorated functions under this decorator.
def migration_implemented(func: Callable):
    @wraps(func)
    def inner(self_instance, *args, **kwargs):
        if type(self_instance) is not Database:
            raise TypeError(
                "Decorator migration_implemented cannot be"
                f" applied to type {type(self_instance)}")
        elif not self_instance.migration:
            error_message = "Migrate object hasn't been implemented yet"
            raise AttributeError(error_message)
        else:
            return func(self_instance, *args, **kwargs)
    return inner




class Database(Service):
    """Operates over database processes."""
    # Helper references for shorter writing at ORMs.
    # Ignore lines added for a workaround to fix issue:
    # https://github.com/microsoft/pylance-release/issues/187
    native_database = SQLAlchemy(model_class=Orm)
    Orm: Any = native_database.Model
    column = native_database.Column
    integer = native_database.Integer
    string = native_database.String
    text = native_database.Text
    float = native_database.Float
    boolean = native_database.Boolean
    foreign_key = native_database.ForeignKey
    table = native_database.Table
    check_constraint = native_database.CheckConstraint
    relationship = native_database.relationship
    backref = native_database.backref
    pickle = native_database.PickleType
    binary = native_database.LargeBinary
    datetime = native_database.DateTime

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self.DEFAULT_URI = f"sqlite:///{self.config['root_dir']}/sqlite3.database"

        self.native_database = Database.native_database
        # For now service config propagated to Database domain
        self._assign_uri_from_config(config)

    def _assign_uri_from_config(self, config: dict) -> None:
        raw_uri = config.get("uri", None)  # type: str

        if not raw_uri:
            log.info(f"URI for database is not specified, using default")
            raw_uri = self.DEFAULT_URI
        else:
            # Case 1: SQLite Database
            # Developer can give relative path to the Database
            # (it will be absolutized at Config.parse()),
            # by setting sqlite Database extension to `.database`, e.g.:
            #   `./instance/sqlite3.database`
            # or by setting full absolute path with protocol, e.g.:
            #   `sqlite:////home/user/project/instance/sqlite3.database`
            if raw_uri.rfind(".database") != -1 or "sqlite:///" in raw_uri:
                if "sqlite:///" not in raw_uri:
                    # Set absolute path to database
                    # Ref: https://stackoverflow.com/a/44687471/14748231
                    self.uri = "sqlite:///" + raw_uri
                else:
                    self.uri = raw_uri
                self.type_enum = DatabaseTypeEnum.SQLITE
            # Case 2: PostgreSQL Database
            elif re.match(r"postgresql(\+\w+)?://", raw_uri):
                # No need to calculate path since psql uri should be given in
                # full form
                self.uri = raw_uri
                self.type_enum = DatabaseTypeEnum.PSQL
            else:
                raise ValueError(
                    "Unrecognized or yet unsupported type of Database uri:"
                    f" {raw_uri}")

            # WARNING:
            #   Never print full Database uri to config, since it may
            #   contain user's password (as in case of psql)
            log.info(f"Set database type: {self.type_enum.value}")

    @migration_implemented
    def init_migration(
            self,
            directory: str = "migrations",
            multidatabase: bool = False) -> None:
        """Initializes migration support for the application."""
        flask_migrate.init(directory=directory, multidb=multidatabase)

    @migration_implemented
    def migrate_migration(
        self,
        directory: str = "migrations",
        message = None,
        sql = False,
        head: str = "head",
        splice = False,
        branch_label = None,
        version_path = None,
        rev_id = None
    ) -> None:
        flask_migrate.migrate(
            directory=directory,
            message=message,
            sql=sql,
            head=head,
            splice=splice,
            branch_label=branch_label,
            version_path=version_path,
            rev_id=rev_id
        )

    @migration_implemented
    def upgrade_migration(
        self,
        directory: str = "migrations",
        revision: str = "head",
        sql = False,
        tag = None
    ) -> None:
        flask_migrate.upgrade(
            directory=directory,
            revision=revision,
            sql=sql,
            tag=tag
        )

    def setup(self, flask_app: Flask) -> None:
        """Setup Database and migration object with given Flask app."""
        flask_app.config["SQLALCHEMY_DATABASE_URI"] = self.uri
        flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        self.native_database.init_app(flask_app)

        # render_as_batch kwarg required only for sqlite3 databases to avoid
        # ALTER TABLE issue on migrations
        # https://blog.miguelgrinberg.com/post/fixing-alter-table-errors-with-flask-migrate-and-sqlite
        if self.type_enum is DatabaseTypeEnum.SQLITE:
            is_sqlite_database = True
        else:
            is_sqlite_database = False
        self.migration = flask_migrate.Migrate(
            flask_app, self.native_database, render_as_batch=is_sqlite_database
        )

    def get_native_database(self) -> SQLAlchemy:
        return self.native_database

    @migration_implemented
    def get_migration(self) -> flask_migrate.Migrate:
        """Return migration object.

        Raise:
            AttributeError: If Migrate object hasn't implemented yet.
        """
        return self.migration

    @migration_implemented
    def create_all(self) -> None:
        self.native_database.create_all()

    @migration_implemented
    def drop_all(self):
        """Drop all tables."""
        self.native_database.drop_all()

    @migration_implemented
    def add(self, *entities):
        """Place an object in the session."""
        for entity in entities:
            self.native_database.session.add(entity)

    @migration_implemented
    def delete(self, *entities):
        for entity in entities:
            self.native_database.session.delete(entity)

    @migration_implemented
    def push(self, *entities):
        """Add entity to session and immediately commit the session."""
        for entity in entities:
            self.add(entity)
        self.commit()

    @migration_implemented
    def refresh(self, *entities):
        for entity in entities:
            self.native_database.session.refresh(entity)

    @migration_implemented
    def expire(self, *entities):
        for entity in entities:
            self.native_database.session.expire(entity)

    @migration_implemented
    def refpush(self, *entities):
        self.push(*entities)
        self.refresh(*entities)

    @migration_implemented
    def flush(self):
        self.native_database.session.flush()

    @migration_implemented
    def commit(self):
        """Commit current transaction."""
        self.native_database.session.commit()

    @migration_implemented
    def rollback(self):
        self.native_database.session.rollback()

    @migration_implemented
    def remove(self):
        self.native_database.session.remove()
