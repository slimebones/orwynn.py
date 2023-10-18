from queue import Empty, Queue
from typing import Self

from antievil import LogicError
from sqlalchemy import select
from sqlalchemy.orm import Session

from orwynn.sql.errors import (
    EmptyExecutionQueueError,
    ManageableSHDError,
    NonManageableSHDError,
    SqlToUpstreamUnmatchError,
)
from orwynn.sql.sql import SQL
from orwynn.utils.func import FuncSpec


class SHD:
    """
    Special shell for a session.

    If "shd" is None, a new session is created using the given
    Sql service. In this case on context exit, the session will be
    automatically closed. If "shd" is not None, an error will be raised
    on session closing actions (like commit(), rollback() or close()) to
    not break an upstream session management processes.

    All session-significant actions, such as "add", "delete", "commit" and
    "rollback" is not made for an upstream session, but instead, non-closing
    actions like add() and delete(), are added to an execution queue, which
    can be then invoked at main SHD using execute() method. Such method cannot
    be called by SHD which have been accepted an upstream session, but adding
    new calls to such SHD will be propagated to it's upstream session.

    An example for main thread:
    ```python
    def main():
        my_shd = SHD.new(sql)

        donut = donut_service.create_donut(
            my_shd,
            name="best donut"
        )
        bakery = bakery_service.create_bakery(
            my_shd,
            donut_ids=donut_id
        )
        # note that neither donut nor bakery don't have an
        # id yet, since are not commited and refreshed, due
        # to giving an upstream shd to the services

        some_service.delete_item("1234", my_shd)

        my_shd.execute()
        # call list:
        # shd.add(donut)
        # (ignored) shd.commit()
        # (ignored) shd.refresh(donut)
        #
        # shd.add(bakery)
        # (ignored) shd.commit()
        # (ignored) shd.refresh(bakery)
        #
        # shd.delete(item)

        my_shd.commit()
        my_shd.close()
    ```
    """
    def __init__(
        self,
        # sql object can be None but only if upstream_shd is not None
        sql: SQL | None,
        # shd is not set to None by default since it encourages to consider
        # an upstream shd object (e.g. which came as an argument)
        upstream_shd: Self | None,
    ) -> None:
        self.__is_manageable: bool
        self._target_session: Session

        self._execution_queue: "Queue[FuncSpec]" = Queue()
        self.__upstream_shd: SHD | None = upstream_shd

        if self.__upstream_shd is None:
            if sql is None:
                raise SqlToUpstreamUnmatchError
            self._target_session = sql.session
            self.__is_manageable = True
        else:
            self._target_session = self.__upstream_shd.target_session
            self.__is_manageable = False

        # Mirror methods #
        self.scalar = self._target_session.scalar
        self.scalars = self._target_session.scalars
        self.select = select
        self.get = self._target_session.get
        self.query = self._target_session.query
        self.execute_statement = self._target_session.execute
        ##

    def __enter__(self) -> Self:
        return self

    def __exit__(self, type, value, traceback):
        if self.is_manageable:
            self.close()

    @property
    def target_session(self) -> Session:
        return self._target_session

    @property
    def is_manageable(self) -> bool:
        return self.__is_manageable

    @classmethod
    def new(cls, sql: SQL) -> Self:
        """
        Creates a new manageable SHD without an upstream object.

        Args:
            sql:
                Sql object to work with.

        Returns:
            A new SHD created.
        """
        return cls(sql, None)

    @classmethod
    def inherit(cls, upstream: Self) -> Self:
        """
        Creates a new non-manageable SHD with an upstream object.
        """
        return cls(None, upstream)

    def refresh(self, *args) -> None:
        """
        Refresh one or more tables from database.
        """
        if self.is_manageable:
            for arg in args:
                self._target_session.refresh(arg)
        else:
            raise NonManageableSHDError(
                operation_name="refresh",
            )

    def add(self, instance: object, _warn: bool = True) -> None:
        if self.__is_manageable:
            self._target_session.add(instance, _warn)
        else:
            self._add_to_execution_queue(FuncSpec(
                fn=self._target_session.add,
                args=(
                    instance,
                    _warn,
                ),
            ))

    def queue(self, fnspec: FuncSpec) -> None:
        """
        Adds a function to execution queue.

        Useful for addding operations like `parent.children.append(child1)` to
        execute it later without getting an empty queue error.
        """
        if self.is_manageable:
            raise ManageableSHDError(
                operation_name="queue",
            )
        self._add_to_execution_queue(fnspec)

    def delete(self, instance: object) -> None:
        if self.__is_manageable:
            self._target_session.delete(instance)
        else:
            self._add_to_execution_queue(FuncSpec(
                fn=self._target_session.delete,
                args=(
                    instance,
                ),
            ))

    def commit(self) -> None:
        if self.__is_manageable:
            self._target_session.commit()
        else:
            raise NonManageableSHDError(
                operation_name="commit",
            )

    def rollback(self) -> None:
        if self.__is_manageable:
            self._target_session.rollback()
        else:
            raise NonManageableSHDError(
                operation_name="rollback",
            )

    def close(self) -> None:
        if self.__is_manageable:
            self._target_session.close()
        else:
            raise NonManageableSHDError(
                operation_name="close",
            )

    def execute(self) -> None:
        """
        Executes all writing functions stored in execution queue.

        Can be called only from manageable SHD.
        """
        if not self.__is_manageable:
            raise NonManageableSHDError(
                operation_name="execute",
            )
        elif self._execution_queue.empty():
            # TODO(ryzhovalex): raising this error here breaks isolation OOP
            #   principle because the caller need to known whether the caller
            #   function executed any execution queue additions, need to think
            #   how to better handle this
            # 0
            raise EmptyExecutionQueueError
        else:
            while True:
                try:
                    fn_spec: FuncSpec = self._execution_queue.get_nowait()
                    fn_spec.call()
                except Empty:
                    return

    def execute_final(self) -> None:
        """
        Executes queue and calls commit on success.
        """
        self.execute()
        self.commit()

    def _add_to_execution_queue(
        self,
        fn_spec: FuncSpec,
    ) -> None:
        """
        Adds a fn spec to execution queue of this SHD, or of upstream one if
        it exists.
        """
        if self.__is_manageable:
            self._execution_queue.put_nowait(fn_spec)
        elif self.__upstream_shd is None:
            raise LogicError(
                f"shd={self} is not manageable, but an upstream shd is None",
            )
        else:
            self.__upstream_shd._add_to_execution_queue(
                fn_spec,
            )
