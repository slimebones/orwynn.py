from sqlalchemy.orm import Mapped, mapped_column

from orwynn.sql.table import Table


class StateFlag(Table):
    """
    Holds some flag signifies state of database.
    """
    name: Mapped[str] = mapped_column(unique=True)
    value: Mapped[bool]
