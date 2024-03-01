from collections.abc import Callable
from typing import TYPE_CHECKING

import typing_extensions
from pykit import validation
from pykit.cls import Static
from pykit.errors import NotFoundError
from sqlalchemy import Select, text

from orwynn.app import AppMode
from orwynn.di.di import Di
from orwynn.log import Log
from orwynn.model import Model
from orwynn.proxy.boot import BootProxy
from orwynn.sql.constants import PSQLStatementConstants
from orwynn.sql.search import TableSearch
from orwynn.sql.shd import SHD
from orwynn.sql.sql import SQL
from orwynn.sql.stateflag import StateFlag
from orwynn.sql.table import Table
from orwynn.sql.types import ConvertedModel, ListedConvertedModel, TTable

if TYPE_CHECKING:
    from collections.abc import Sequence


class SHDUtils(Static):
    @classmethod
    def scalars_all(
        cls,
        selection: Select[tuple[TTable]],
        search: TableSearch[TTable],
        shd: SHD | None = None,
    ) -> list[TTable]:
        """
        Executes a selection statement and returns result as all scalars.

        Args:
            selection:
                Selection to execute.
            search:
                What search is performed to produce given selection statement.
            shd(optional):
                Explicitly given SHD in case if search was performed using
                internal SHD. Defaults to search's SHD, i.e. external one.
        """
        final_shd: SHD = shd if shd is not None else search.get_shd()

        result: Sequence[TTable] | None = final_shd.scalars(
            selection,
        ).all()

        if not result:
            # we just give "T" here as a title since i don't want to
            # investigate generic's name retrieval in Python -- ryzhovalex
            raise search.get_not_found_error("TTable")
        if search.expectation is not None:
            search.expectation.check(result)

        return list(result)


class SQLUtils(Static):
    @staticmethod
    @typing_extensions.deprecated("use sql.recreate_public_schema_cascade")
    def drop_database(
        sql: SQL,
    ) -> None:
        if (
            sql.should_drop_sql
            # lock drop in prod mode for error-protection
            and BootProxy.ie().mode != AppMode.PROD
        ):
            Log.info("drop sql database")
            # use raw sql since i haven't found a quick way to drop cascade
            # using python objects
            with sql.session as s:
                s.execute(text(
                    PSQLStatementConstants.RecreatePublicSchemaCascade
                ))
                s.commit()

    @staticmethod
    def get_state_flag_by_name(
        name: str,
        shd: SHD,
    ) -> StateFlag:
        check.instance(name, str)

        result: StateFlag | None = shd.scalar(
            shd.select(StateFlag).where(
                StateFlag.name == name,
            ),
        )

        if not result:
            raise NotFoundError(
                title="state flag",
                options={
                    "name": name,
                },
            )

        return validation.apply(
            result,
            StateFlag,
        )

    @staticmethod
    def set_state_flag_by_name(
        name: str,
        value: bool,
        shd: SHD,
    ) -> StateFlag:
        """
        Finds a state flag by name and sets a new value to it.
        """
        check.instance(name, str)
        check.instance(value, bool)

        state_flag: StateFlag = SQLUtils.get_state_flag_by_name(name, shd)
        state_flag.value = value

        return state_flag

    @staticmethod
    def get_one(
        id: str,
        Table_: type[TTable],
        shd: SHD,
    ) -> TTable:
        """Finds table row with given id.

        Works similar as sqlalchemy.shd.get(), but with id.

        Args:
            id:
                Id to match.
            Table_:
                Table to search within.
            session:
                SqlA shd.

        Returns:
            Table row found.
        """
        check.instance(id, str)
        check.instance(Table_, Table)
        check.instance(shd, SHD)

        result: TTable | None = shd.scalar(
            shd.select(Table_).where(
                Table_.id == id,
            ),
        )

        if not result:
            raise NotFoundError(
                title="table",
                options={
                    "id": id,
                },
            )

        return validation.apply(
            result,
            Table_,
        )

    @staticmethod
    def get_all_by_ids(
        ids: list[str],
        Table_: type[TTable],
        shd: SHD,
    ) -> list[TTable]:
        """Finds all table rows using list of ids.

        Args:
            ids:
                Ids to find.
            Table_:
                Table to search within.
            session:
                SqlA shd.

        Returns:
            Table rows found.
        """
        check.instance(ids, list)

        rows: list[TTable] = []

        for id in ids:
            rows.append(
                SQLUtils.get_one(id, Table_, shd),
            )

        return rows

    @staticmethod
    def get_one_and_convert(
        id: str,
        Table_: type[TTable],
        convertion_func: Callable[[TTable], ConvertedModel],
        shd: SHD,
    ) -> ConvertedModel:
        """
        Find one row and converts it into model using convertion function.

        Args:
            id:
                Id to match.
            Table_:
                Table where object resides.
            convertion_func:
                Convertion function to be used to convert Table->Model.
            session:
                SqlA shd.

        Returns:
            Converted model.
        """
        check.instance(Table_, Table)
        check.instance(convertion_func, Callable)
        check.instance(shd, SHD)

        return convertion_func(SQLUtils.get_one(
            id,
            Table_,
            shd,
        ))

    @staticmethod
    def get_all_and_convert(
        Table_: type[TTable],
        convertion_func: Callable[[TTable], ConvertedModel],
        ListedConvertedModel_: type[ListedConvertedModel],
        listed_converted_model_units_key: str,
        shd: SHD,
    ) -> ListedConvertedModel:
        """
        Finds all rows for table and converts them into listed model (model
        that contains many converted models).

        Args:
            Table_:
                Table where object resides.
            convertion_func:
                Convertion function to be used to convert Table->Model.
            ListedConvertedModel_:
                Model to be used as a container for all converted models.
            listed_converted_model_units_key:
                Key of the ListedConvertedModel_ where collected units should
                be passed. For example "products".
            session:
                SqlA shd.

        Returns:
            Listed model with converted models.
        """
        check.instance(Table_, Table)
        check.instance(convertion_func, Callable)
        check.instance(ListedConvertedModel_, Model)
        check.instance(listed_converted_model_units_key, str)
        check.instance(shd, SHD)

        rows: list[TTable] = SQLUtils.get_all(
            Table_,
            shd,
        )
        converted_list: list[ConvertedModel] = []
        for row in rows:
            converted_list.append(convertion_func(row))
        return ListedConvertedModel_.parse_obj({
            listed_converted_model_units_key: converted_list,
        })

    @staticmethod
    def get_all(
        Table_: type[TTable],
        shd: SHD,
        *,
        ids: list[str] | None = None,
    ) -> list[TTable]:
        """
        Find all rows for table.

        Args:
            Table_:
                Table to search within.
            session:
                SqlA shd.
            ids (optional):
                List of ids for which to found tables.

        Returns:
            All rows for table.
        """
        check.instance(shd, SHD)
        check.instance(Table_, Table)

        selection = shd.select(Table_)

        if ids:
            selection = selection.where(
                Table_.id.in_(ids),
            )

        result: Sequence[TTable] | None = shd.scalars(
            selection,
        ).all()

        if not result:
            raise NotFoundError(
                title="table",
                options={
                    "ids": ids,
                },
            )

        tables: list[TTable] = list(result)
        check.instance_each(tables, Table)

        return tables

    @staticmethod
    def get_sql_from_di(di: Di) -> SQL:
        return validation.apply(di.find("SQL"), SQL)

    @staticmethod
    def create_tables(sql: SQL):
        sql.create_tables()
