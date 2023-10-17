import pytest
from orwynn.boot import Boot
from orwynn.bootscript import Bootscript, CallTime
from orwynn.di.di import Di
from orwynn.sql import SQL, Table
from orwynn.sql.table import Mapped

from orwynn.utils.dbsearch import TableSearch
from orwynn.utils.usql._helpers import create_tables
from orwynn.utils.usql.shd import SHD


class S1Item(Table):
    name: Mapped[str]
    price: Mapped[float]


@pytest.fixture
def create_tables_bootscript() -> Bootscript:
    return Bootscript(
        fn=create_tables,
        call_time=CallTime.AFTER_ALL,
    )


@pytest.fixture
def s1_search(bare_boot: Boot) -> TableSearch:
    sql: SQL = Di.ie().find("Sql")
    return TableSearch(
        ids=["a", "b", "c"],
        shd=SHD.new(sql),
    )
