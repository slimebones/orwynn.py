from typing import Generic, Literal, Self

from antievil import NameExpectError, UnsupportedError

from orwynn.sql.shd import SHD
from orwynn.sql.table import Table
from orwynn.sql.types import TTable
from orwynn.utils.dbsearch import DatabaseSearch


class TableSearch(DatabaseSearch[Table], Generic[TTable]):
    """
    Base search terms to find SQL tables.

    Used as a main argument to most Repo table getters.
    """
    shd: SHD | Literal["internal"]
    """
    Session handler of the search.

    Can be set to literal "internal" signifying that a search is meant to work
    with callable's internal SHD. This is a typical case when working e.g. with
    DTO's repos, which methods work only with internal shds in order to bake
    correct dto models on return.
    """

    class Config:
        arbitrary_types_allowed = True

    def get_shd(self) -> SHD:
        if isinstance(self.shd, SHD):
            return self.shd
        raise UnsupportedError(
            title="for external using, search shd",
            value=self.shd,
        )

    def check_internal(self) -> None:
        if self.shd != "internal":
            raise NameExpectError(
                objinfo=("shd", self.shd),
                name="internal",
            )

    def activate_shd(self, shd: SHD) -> Self:
        """
        Return copy of self with SHD's activated.

        Only works for search models with shd="internal".
        """
        if self.shd != "internal":
            raise UnsupportedError(
                title="activating shd for search with existing shd",
                value=shd,
            )
        return self.copy(update={"shd": shd})
