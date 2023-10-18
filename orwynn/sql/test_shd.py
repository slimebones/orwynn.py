from typing import overload

import pytest
from antievil import NotFoundError

from orwynn import sql
from orwynn.base import Module, Service
from orwynn.boot import Boot
from orwynn.bootscript import Bootscript
from orwynn.di.di import Di
from orwynn.sql import SQL
from orwynn.sql.errors import EmptyExecutionQueueError
from orwynn.sql.shd import SHD
from orwynn.sql.testing import S1Item
from orwynn.sql.utils import SQLUtils
from orwynn.utils import validation


class ItemRepo(Service):
    def __init__(self, sql: SQL) -> None:
        super().__init__()

        self._sql: SQL = sql

    def get_one(
        self,
        id: str,
        shd: SHD,
    ) -> S1Item:
        return SQLUtils.get_one(id, S1Item, shd)

    @overload
    def create_one(
        self,
        shd: None = None,
        *,
        name: str,
        price: float,
    ) -> str: ...

    @overload
    def create_one(
        self,
        shd: SHD,
        *,
        name: str,
        price: float,
    ) -> S1Item: ...

    def create_one(
        self,
        shd: SHD | None = None,
        *,
        name: str,
        price: float,
    ) -> S1Item | str:
        with SHD(self._sql, shd) as _shd:
            item: S1Item = S1Item(name=name, price=price)

            _shd.add(item)

            if _shd.is_manageable:
                _shd.commit()
                _shd.refresh(item)
                return item.id
            else:
                return item

    @overload
    def delete_one(
        self,
        id: str,
        shd: SHD,
    ) -> S1Item: ...

    @overload
    def delete_one(
        self,
        id: str,
        shd: None = None,
    ) -> None: ...

    def delete_one(
        self,
        id: str,
        shd: SHD | None = None,
    ) -> S1Item | None:
        with SHD(self._sql, shd) as _shd:
            item: S1Item = self.get_one(id, _shd)

            _shd.delete(item)

            if _shd.is_manageable:
                _shd.commit()
                return None
            else:
                return item


@pytest.mark.asyncio
async def test_execution_normal(
    create_tables_bootscript: Bootscript,
):
    await Boot.create(
        Module(
            Providers=[ItemRepo],
            imports=[sql.module],
        ),
        bootscripts=[
            create_tables_bootscript,
        ],
        apprc={
            "prod": {
                "SQL": {
                    "database_kind": "sqlite",
                    "database_path": ":memory:"
                }
            }
        }
    )

    item_repo: ItemRepo = Di.ie().find("ItemRepo")

    with SHD.new(Di.ie().find("SQL")) as shd:
        created_item_id: str = item_repo.create_one(name="donut", price=1.2)
        created_item: S1Item = item_repo.get_one(created_item_id, shd)

        validation.expect(
            shd.execute_final,
            EmptyExecutionQueueError,
        )

        assert created_item.name == "donut"
        assert created_item.price == 1.2

        item_repo.delete_one(created_item.id)

        validation.expect(
            shd.execute_final,
            EmptyExecutionQueueError,
        )

        validation.expect(
            item_repo.get_one,
            NotFoundError,
            created_item.id,
            shd,
        )


@pytest.mark.asyncio
async def test_execution_upstream(
    create_tables_bootscript: Bootscript,
):
    await Boot.create(
        Module(
            Providers=[ItemRepo],
            imports=[sql.module],
        ),
        bootscripts=[create_tables_bootscript],
        apprc={
            "prod": {
                "SQL": {
                    "database_kind": "sqlite",
                    "database_path": ":memory:"
                }
            }
        }
    )

    item_repo: ItemRepo = Di.ie().find("ItemRepo")

    with SHD.new(Di.ie().find("SQL")) as shd:
        created_item: S1Item = item_repo.create_one(
            shd, name="donut", price=1.2,
        )
        created_item.price = created_item.price + 0.5

        shd.execute_final()
        shd.refresh(created_item)

        assert isinstance(created_item.id, str)
        assert created_item.name == "donut"
        assert created_item.price == 1.7

        deleted_item_id: str = item_repo.delete_one(created_item.id, shd).id

        shd.execute_final()

        validation.expect(
            item_repo.get_one,
            NotFoundError,
            deleted_item_id,
            shd,
        )
