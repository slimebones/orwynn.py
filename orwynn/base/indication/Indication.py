from typing import Any, ItemsView
from orwynn.base.error.Error import Error
from orwynn.base.error.ErrorSchemaValue import ErrorSchemaValue

from orwynn.base.indication.Indicator import Indicator
from orwynn.base.SUBCLASSABLES import SUBCLASSABLES
from orwynn.base.BaseSubclassable import BaseSubclassable
from orwynn.base.indication.digesting_error import DigestingError
from orwynn.base.indication.Indicatable import Indicatable, IndicatableClass
from orwynn.base.indication.unsupported_indicator_error import \
    UnsupportedIndicatorError
from orwynn.base.model.Model import Model
from orwynn.util.cls import ClassNotFoundError, find_subclass_by_name
from orwynn.util.mp.location import (FieldLocation, find_field_by_location,
                                     find_location_by_field)
from orwynn.util.validation import validate, validate_dict
from orwynn.util.validation.validator import Validator
from orwynn.util.web import HTTPException

_Locations = dict[Indicator, FieldLocation]


class Indication:
    """Holds some representation of how the data should be built like to serve
    as an convention for building objects.

    Each indication is simply mapping between strings and Indicators, but also
    implements special digest_* methods to transform given object applying
    defined indication rules.

    Also has counter-methods recover_* to create object back from dictionary.

    Strings-only as keys are used for an additional constraints for objects
    building an API structures, in future it is possible to see here an
    additional flags controlling this behaviour.

    For the list of applicable types see Indicator.
    """
    def __init__(
        self,
        mp: dict[str, Indicator]
    ) -> None:
        # FIXME: Temporarily indicators should be placed at highest dictionary
        #   level
        validate_dict(
            mp, (str, Indicator)
        )

        self.__mp: dict[str, Indicator] = mp
        self.__locations: _Locations = self.__find_locations()
        self.__created_schema_by_name: dict[str, type[Model]] = {}

    def gen_schema(
        self,
        Entity: IndicatableClass
    ) -> type[Model]:
        schema_name: str = Entity.__name__ + "IndicationSchema"
        schema_kwargs: dict[str, Any] = {}

        for k, v in self.items:
            final_field: str | type
            match v:
                case Indicator.TYPE:
                    final_field = str
                case Indicator.VALUE:
                    if (
                        issubclass(Entity, Exception)
                        and not issubclass(Entity, Error)
                    ):
                        final_field = ErrorSchemaValue
                    elif issubclass(Entity, Error):
                        final_field = ErrorSchemaValue
                    elif issubclass(Entity, Model):
                        final_field = Entity
                    else:
                        raise TypeError(
                            f"unsupported obj type {type(Entity)}"
                        )
                case _:
                    raise UnsupportedIndicatorError(
                        f"indicator {v} is not supported"
                    )
            schema_kwargs[k] = (final_field, ...)

        try:
            return self.__created_schema_by_name[schema_name]
        except KeyError:
            CreatedModel: type[Model] = Model.create_dynamic(
                schema_name,
                **schema_kwargs
            )
            self.__created_schema_by_name[schema_name] = CreatedModel
            return CreatedModel

    def __find_locations(self) -> _Locations:
        return {
            Indicator.TYPE: find_location_by_field(Indicator.TYPE, self.__mp),
            Indicator.VALUE: find_location_by_field(Indicator.VALUE, self.__mp)
        }

    @property
    def items(self) -> ItemsView[str, Indicator]:
        return self.__mp.items()

    def digest(self, obj: Indicatable) -> dict:
        """Traverses object to create dictionary based on defined
        indicators.

        Args:
            obj:
                Object to be digested.

        Returns:
            Dictionary with keys and values complying this indication.

        Raises:
            UnsupportedIndicatorError:
                Occured indicator is not supported.
        """
        result: dict = {}

        is_type_indicator_found: bool = False
        is_value_indicator_found: bool = False

        for k, v in self.items:
            final_field: str | dict
            match v:
                case Indicator.TYPE:
                    final_field = obj.__class__.__name__
                    is_type_indicator_found = True
                case Indicator.VALUE:
                    if isinstance(obj, HTTPException):
                        final_field = {
                            "status_code": obj.status_code,
                            "message": obj.detail
                        }
                    elif (
                        isinstance(obj, Exception)
                        and not isinstance(obj, Error)
                    ):
                        final_field = {
                            "message": "; ".join([str(x) for x in obj.args])
                        }
                    elif isinstance(obj, Error) or isinstance(obj, Model):
                        final_field = obj.dict()
                    else:
                        raise TypeError(
                            f"unsupported obj type {type(obj)}"
                        )
                    is_value_indicator_found = True
                case _:
                    raise UnsupportedIndicatorError(
                        f"indicator {v} is not supported"
                    )
            result[k] = final_field

        if not is_type_indicator_found:
            raise DigestingError(
                f"indication {self} should contain indicator {Indicator.TYPE}"
                f" and {Indicator.VALUE} in any fields to be able to digest"
                " models"
            )

        if not is_value_indicator_found:
            raise DigestingError(
                "wasn't able to find Indicator.VALUE related field"
            )

        return result

    def recover(self, mp: dict) -> BaseSubclassable | Exception:
        """Creates object from given map according to indication rules.

        Note that your project's indication instance should match an indication
        instance used to digest the object.

        Only instances of base classes subclasses can be recovered. E.g.
        Model or Error.

        Recovering of Python's Exception are also supported.

        Args:
            mp:
                Dictionary from which object will be recovered.

        Returns:
            Recovered object.

        Raises:
            RecoveringError:
                TYPE or VALUE locations of given dictionary are not matched
                with according indication data.
        """
        validate_dict(mp, (str, Validator.SKIP))

        TargetClass: type = self.__find_type_in_mp(mp)
        value: dict = self.__find_value_in_mp(mp)

        if (
            issubclass(TargetClass, HTTPException)
        ):
            return TargetClass(
                status_code=value["status_code"],
                detail=value["message"]
            )
        elif (
            issubclass(TargetClass, Exception)
            and not issubclass(TargetClass, Error)
        ):
            return TargetClass(*value["message"].split("; "))
        else:
            return TargetClass(**value)

    def recover_model_with_type(
        self, ModelType: type[Model], mp: dict
    ) -> Model:
        """Creates model object of given type using given map according to
        indication rules.

        Works the same as recover_model(...), but is faster since knows which
        model type to initialize.

        Args:
            ModelType:
                Type to initialize.
            mp:
                Dictionary from which model will be recovered.

        Returns:
            Recovered model.

        Raises:
            RecoveringError:
                TYPE or VALUE locations of given dictionary are not matched
                with according indication data.
        """
        validate(ModelType, Model)
        validate_dict(mp, (str, Validator.SKIP))

        # Note that in this case availability of Indicator.TYPE field in given
        # map is not checked since only Indicator.VALUE is needed.
        model_value: dict = self.__find_value_in_mp(mp)

        return ModelType.parse_obj(model_value)

    def __find_type_in_mp(self, mp: dict) -> type:
        indication_type_field_location: FieldLocation = \
            self.__locations[Indicator.TYPE]
        mp_type_field: str = find_field_by_location(
            indication_type_field_location, mp
        )
        return self.__find_subclass_by_name_out_of_subclassables(mp_type_field)

    def __find_value_in_mp(self, mp: dict) -> dict:
        indication_value_field_location: FieldLocation = \
            self.__locations[Indicator.VALUE]
        mp_value: dict = find_field_by_location(
            indication_value_field_location, mp
        )

        validate(mp_value, dict)
        return mp_value

    def __find_subclass_by_name_out_of_subclassables(self, name: str) -> type:
        subclass: type | None = None

        # Including Exception in searched classes may take much longer
        for Subclassable in SUBCLASSABLES + [Exception]:
            try:
                subclass = find_subclass_by_name(name, Subclassable)
            except ClassNotFoundError:
                continue
            else:
                return subclass

        raise ValueError(f"subclassable with name {name} not found")
