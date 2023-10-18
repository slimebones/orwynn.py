import pytest

from orwynn.boot import Boot
from orwynn.bootscript import Bootscript, CallTime
from orwynn.di.di import Di
from orwynn.sql import SQL, Table
from orwynn.sql.search import TableSearch
from orwynn.sql.shd import SHD
from orwynn.sql.table import Mapped
from orwynn.sql.utils import SQLUtils


class S1Item(Table):
    name: Mapped[str]
    price: Mapped[float]


@pytest.fixture
def create_tables_bootscript() -> Bootscript:
    return Bootscript(
        fn=SQLUtils.create_tables,
        call_time=CallTime.AFTER_ALL,
    )


@pytest.fixture
def s1_table_search(bare_boot: Boot) -> TableSearch:
    sql: SQL = Di.ie().find("SQL")
    return TableSearch(
        ids=["a", "b", "c"],
        shd=SHD.new(sql),
    )
