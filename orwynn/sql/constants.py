from pykit.cls import Static


class PSQLStatementConstants(Static):
    RecreatePublicSchemaCascade: str = (
        "DROP SCHEMA public CASCADE;"
        " CREATE SCHEMA public;"
    )
