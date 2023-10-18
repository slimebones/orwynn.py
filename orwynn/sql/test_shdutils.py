import pytest
from antievil import NotFoundError

from orwynn.di.di import Di
from orwynn.sql.search import TableSearch
from orwynn.sql.shd import SHD
from orwynn.sql.testing import S1Item
from orwynn.sql.utils import SHDUtils
from orwynn.utils import validation


@pytest.mark.asyncio
async def test_s1(s1_table_search: TableSearch):
    with SHD.new(Di.ie().find("SQL")) as shd:
        validation.expect(
            SHDUtils.scalars_all,
            NotFoundError,
            shd.select(S1Item),
            s1_table_search,
        )
