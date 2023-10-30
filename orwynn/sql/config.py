from typing import Any

from orwynn.base.config import Config
from orwynn.base.error import MalfunctionError
from sqlalchemy.pool import StaticPool, Pool

from orwynn.sql.poolclass import PoolclassStr
from .enums import SQLDatabaseKind


class SQLConfig(Config):
    database_kind: SQLDatabaseKind
    database_name: str | None = None
    database_user: str | None = None
    database_password: str | None = None
    database_path: str | None = None
    database_host: str | None = None
    database_port: int | None = None
    poolclass: PoolclassStr | None = None
    pool_size: int | None = None

    def __init__(self, **data: Any) -> None:
        try:
            db_kind: SQLDatabaseKind = SQLDatabaseKind(data["database_kind"])
        except KeyError:
            # memory sqlite is used by default
            db_kind = SQLDatabaseKind.SQLite
            data["database_path"] = ":memory:"

        # Check right associations
        if db_kind is SQLDatabaseKind.PostgreSQL:
            for key in [
                "database_name",
                "database_user",
                "database_password",
                "database_host",
                "database_port"
            ]:
                if not data.get(key, None):
                    raise ValueError(
                        f"for PostgreSQL you should define {key} in SQL config"
                    )
        elif db_kind is SQLDatabaseKind.SQLite:
            if not data.get("database_path", None):
                raise ValueError(
                    "for SQLite you should define database_path in SQL config"
                )
        else:
            raise MalfunctionError()

        super().__init__(**data)

    @property
    def real_poolclass(self) -> type[Pool] | None:
        if self.poolclass is None:
            return None

        match self.poolclass:
            case "StaticPool":
                return StaticPool
            case _:
                raise ValueError()
