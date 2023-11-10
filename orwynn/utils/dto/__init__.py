from collections.abc import Callable, Sequence
from typing import Any, ClassVar, Self, TypeVar

from antievil import NotFoundError, RequiredClassAttributeError

from orwynn.base.model import Model
from orwynn.utils import validation
from orwynn.utils.dto.errors import (
    AbstractDtoClassAsBaseDtoError,
    HasCodeButNoAttributeDtoError,
    UnmatchedCodeFieldDtoError,
)
from orwynn.utils.klass import ClassUtils, Static
from orwynn.websocket import Websocket

_TTable = TypeVar("_TTable")
_TUnitDTO = TypeVar("_TUnitDTO", bound="UnitDTO")
DtoTypes = dict[str, type[_TUnitDTO]]


class DTO(Model):
    """
    Abstract class for Data Transfer Object.
    """


class UnitDTO(DTO):
    """
    Represents some business unit wrapped in DTO to be returned outside.

    Note that model's field "code" is set internally only according to
    class attribute "CODE" (see below).

    So on given "code" field explicitly on model's creation, the
    ValueError will be raised, if the given code is not matched class's CODE.
    In any other case, this argument will be just ignored.

    Class-attributes:
        CODE:
            Type of the dto which will be set at serialization time to field
            "type". Useful to represent different types in interfaces which
            act polymorphically and may return different types of the same
            parent. Defaults to None, i.e. not set.
    """
    Code: ClassVar[str | None] = None
    id: str
    code: str | None = None

    def __init__(self, **data: Any) -> None:
        if "code" in data and data["code"] is not None:
            if self.Code is None:
                raise HasCodeButNoAttributeDtoError(
                    code_field=data["code"],
                )
            elif data["code"] != self.Code:
                raise UnmatchedCodeFieldDtoError(
                    code_field=data["code"],
                    code_attribute=self.Code,
                )

        data["code"] = self.Code

        super().__init__(**data)


class ContainerDTO(DTO):
    """
    Holds a sequence of dto units.

    Class-attributes:
        BASE:
            Instances of which base type (or it's subclasses) will be stored
            in the container. Accepts only UnitDto.
    """
    Base: ClassVar[type[UnitDTO] | None] = None
    units: Sequence[UnitDTO]

    @classmethod
    def _get_base_attr(cls) -> type[UnitDTO]:
        if cls.Base is None:
            raise RequiredClassAttributeError(
                attribute_name="BASE",
                Class=cls,
            )
        elif cls.Base is DTO:
            raise AbstractDtoClassAsBaseDtoError
        else:
            return cls.Base

    @classmethod
    def convert(
        cls,
        tables: list[_TTable],
        convertion_fn: Callable[[_TTable], _TUnitDTO],
        container_kwargs: dict[str, Any] | None = None,
    ) -> Self:
        Base: type[UnitDTO] = cls._get_base_attr()

        result: list[_TUnitDTO] = []

        for table in tables:
            converted: _TUnitDTO = convertion_fn(table)
            validation.validate(converted, Base)
            result.append(converted)

        if not container_kwargs:
            container_kwargs = {}
        return cls(units=result, **container_kwargs)

    @classmethod
    def recover_polymorph(
        cls,
        data: dict,
    ) -> Self:
        """
        Recovers using polymorph strategy setting self as a base parent.

        Args:
            data:
                Dto-compliant raw data.
        """
        Base: type[UnitDTO] = cls._get_base_attr()

        return cls(
            units=DTOUtils.recover_polymorph_units(
                Base=Base,
                units=data["value"]["units"],
            ),
        )


class WebsocketCallDTO(DTO):
    """
    Any call passed in websocket protocol.

    It could be either client's or server's origin.
    """
    websocket: Websocket

    class Config:
        arbitrary_types_allowed = True


class DTOUtils(Static):
    @classmethod
    def recover_polymorph_units(
        cls,
        Base: type[_TUnitDTO],
        units: list[dict],
    ) -> Sequence[_TUnitDTO]:
        """
        Recovers list of item dtos of various types using helper dictionary.

        When some Container DTO cannot be recovered in a simple way using
        Model.recover() because of different UnitDto types which can be stored
        inside, this helper function can be used to retrieve correct list of
        different units for such container.

        This helper function will retrieve some subclass from the given Base,
        where TYPE attribute matches specified one in `units` for each item.

        Args:
            Base:
                Base parent class of all dto types that possibly can be
                recovered.
            raw_units:
                Dictionaries with raw data to be processed back into dtos.

        Returns:
            List of recovered item dtos.

        Raises:
            NotFoundError:
                Cannot find code for item's type.
            NotFoundError:
                Dto subclass for given base and item's type is not found.

        Usage example:
        ```python
        units: Sequence[AnimalDto] = recover_polymorph_units(
            Base=AnimalDto,
            units=[
                {
                    "id": "ed11",
                    "type": "cat",
                    "meows": 10
                },
                {
                    "id": "vj12",
                    "type": "dog",
                    "barks": 15
                }
            ]
        )

        animals_dto: AnimalsDto = AnimalsDto(units=units)

        print(animals_dto.units)
        # =>
        # [CatDto(...), DogDto(...)]
        ```
        """
        validation.validate_each(units, dict, expected_sequence_type=list)

        dtos: Sequence[_TUnitDTO] = []

        for raw_item in units:
            validation.validate(raw_item, dict)

            try:
                type_code: str = raw_item["code"]
            except ValueError as error:
                raise NotFoundError(
                    title="item code",
                    value=raw_item["code"],
                ) from error

            DtoClass: type[_TUnitDTO] = cls.find_dto_class_with_type_code(
                type_code,
                Base=Base,
            )

            dto: _TUnitDTO = validation.apply(
                DtoClass.parse_obj(raw_item),
                Base,
            )

            dtos.append(dto)

        return dtos

    @classmethod
    def find_dto_class_with_type_code(
        cls,
        type_code: str,
        Base: type[_TUnitDTO],
    ) -> type[_TUnitDTO]:
        """
        Searches subclasses of the given Base and returns one found with the
        same type as given one.
        """
        base_subclasses: list[type[_TUnitDTO]] = \
            ClassUtils.find_all_subclasses(Base)  # type: ignore

        for subclass in base_subclasses:
            if (
                subclass.Code is not None
                and subclass.Code == type_code
            ):
                return subclass

        raise NotFoundError(
            title="dto subclass",
            options={
                "base": Base,
                "type_code": type_code,
            },
        )
