import pytest
from antievil import NotFoundError
from orwynn.di.di import Di
from orwynn.utils import validation

from orwynn.utils.dbsearch import TableSearch
from orwynn.utils.usql.shd import SHD
from orwynn.utils.usql.testing import S1Item
from orwynn.utils.usql.utils import SHDUtils


@pytest.mark.asyncio
async def test_s1(s1_search: TableSearch):
    with SHD.new(Di.ie().find("Sql")) as shd:
        validation.expect(
            SHDUtils.scalars_all,
            NotFoundError,
            shd.select(S1Item),
            s1_search,
        )
