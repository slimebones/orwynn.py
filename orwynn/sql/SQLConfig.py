
from typing import Any

from orwynn.config.Config import Config

from .SQLDatabaseKind import SQLDatabaseKind


class SQLConfig(Config):
    database_kind: SQLDatabaseKind
    database_name: str | None = None
    database_user: str | None = None
    database_password: str | None = None
    database_path: str | None = None
    database_host: str | None = None
    database_port: int | None = None

    def __init__(self, **data: Any) -> None:
        db_type: SQLDatabaseKind = data["database_type"]

        # Check right associations
        if db_type is SQLDatabaseKind.POSTGRESQL:
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
        elif db_type is SQLDatabaseKind.SQLITE:
            if not data.get("database_path", None):
                raise ValueError(
                    "for SQLite you should define database_path in SQL config"
                )
        else:
            raise

        super().__init__(**data)
