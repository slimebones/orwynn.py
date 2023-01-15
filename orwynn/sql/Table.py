from typing import Any
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from orwynn.fmt import snakefy
from ..rnd import makeid


class Table(DeclarativeBase):
    """Base orm model responsible of holding database model's data and
    it's basic CRUD operations.

    Update representatives are defined individually at each subclass
    (e.g. `set_something()`), and by default accessed via basic model
    alteration, e.g. `MyModel.name = 'Another name'`.
    """
    _id: Mapped[int] = mapped_column(primary_key=True)
    _type: Mapped[str]

    # Do not map Table to actual database table
    __abstract__ = True

    # For each table special string uuid is generated, but it is not a primary
    # key for the performance sake, for details see:
    #   https://stackoverflow.com/a/517591/14748231
    _uuid: Mapped[str] = mapped_column(default=makeid, unique=True)

    @hybrid_property
    def id(self) -> int:
        return self._id

    @hybrid_property
    def type(self) -> str:
        return self._type

    @hybrid_property
    def uuid(self) -> str:
        return self._uuid

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
