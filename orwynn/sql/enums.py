from enum import Enum


class CreateOrUpdateStatus(Enum):
    """
    When instance could have been created or updated depending of whether it
    have been found or not.
    """
    Created = "created"
    Updated = "updated"


class SQLDatabaseKind(Enum):
    PostgreSQL = "postgresql"
    SQLite = "sqlite"
