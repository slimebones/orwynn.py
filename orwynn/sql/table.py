from typing import Any, Self

from sqlalchemy import ForeignKey
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from orwynn.utils.fmt import snakefy
from orwynn.utils.rnd import makeid


class Table(DeclarativeBase):
    """Base orm model responsible of holding database model's data and
    it's basic CRUD operations.

    Update representatives are defined individually at each subclass
    (e.g. `set_something()`), and by default accessed via basic model
    alteration, e.g. `MyModel.name = 'Another name'`.
    """
    # Do not map Table to actual database table
    __abstract__ = True

    # For each table special string id is generated, but it is not a primary
    # key for the performance sake, for details see:
    #   https://stackoverflow.com/a/517591/14748231
    _id: Mapped[str] = mapped_column(default=makeid, unique=True)

    @hybrid_property
    def sid(self) -> int:
        return self._sid

    @declared_attr.cascading  # type: ignore
    def _sid(cls) -> Mapped[int]:
        parent: type[Self] = cls._get_parent_class()
        if parent is Table:
            return mapped_column(primary_key=True)
        else:
            return mapped_column(
                ForeignKey(snakefy(parent.__name__) + "._sid"),
                primary_key=True
            )

    # Declaring _type as class atrribute might be a reason for sqlalchemy to
    # raise a warning, maybe because this field is being redefined by
    # subclasses.
    @declared_attr
    def _type(self) -> Mapped[str]:
        return mapped_column()

    @classmethod
    def _get_parent_class(cls) -> type[Self]:
        bases: tuple[type] = cls.__bases__

        if len(bases) == 1:
            return bases[0]
        elif len(bases) > 1:
            raise ValueError(
                "multiple inheritance for Tables is not supported"
            )
        else:
            raise

    @hybrid_property
    def type(self) -> str:
        return self._type

    @hybrid_property
    def id(self) -> str:
        return self._id

    @declared_attr.directive
    def __tablename__(cls) -> str:
        cls_name: str = cls.__name__
        return snakefy(cls_name)

    @declared_attr.directive
    def __identity__(cls) -> str:
        return snakefy(cls.__name__)

    @declared_attr.directive
    def __mapper_args__(cls) -> dict[str, Any]:
        args: dict[str, Any] = {}
        args.update({
            "polymorphic_on": "_type",
            "polymorphic_identity": cls.__identity__
        })
        return args
