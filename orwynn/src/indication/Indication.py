from enum import Enum
import json
from typing import Any, ItemsView

from orwynn.src.BaseSubclassable import BaseSubclassable
from orwynn.src.error.Error import Error
from orwynn.src.error.ErrorValueSchema import ErrorValueSchema
from orwynn.src.error.HTTPExceptionValueSchema import HTTPExceptionValueSchema
from orwynn.src.error.RequestValidationExceptionValueSchema import \
    RequestValidationExceptionValueSchema
from orwynn.src.indication.IndicationType import IndicationType
from orwynn.src.indication.digesting_error import DigestingError
from orwynn.src.indication.Indicatable import IndicatableTypeVar, Indicatable
from orwynn.src.indication.Indicator import Indicator
from orwynn.src.indication.unsupported_indicator_error import \
    UnsupportedIndicatorError
from orwynn.src.model.Model import Model
from orwynn.src.SUBCLASSABLES import SUBCLASSABLES
from orwynn.src import validation
from orwynn.src.cls.helpers import ClassNotFoundError, find_subclass_by_name
from orwynn.src.mp.location import (FieldLocation, find_field_by_location,
                                     find_location_by_field)
from orwynn.src.validation import (RequestValidationException, validate,
                                    validate_dict)
from orwynn.src.validation.validator import Validator
from orwynn.src.web.http.HttpException import HttpException

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
        Entity: type[IndicatableTypeVar]
    ) -> type[Model]:
        schema_name: str = Entity.__name__ + "IndicationSchema"
        schema_kwargs: dict[str, Any] = {}

        for k, v in self.items:
            final_field: str | type
            match v:
                case Indicator.TYPE:
                    final_field = str
                case Indicator.VALUE:
                    if issubclass(Entity, HttpException):
                        final_field = HTTPExceptionValueSchema
                    elif issubclass(
                        Entity, RequestValidationExceptionValueSchema
                    ):
                        final_field = RequestValidationExceptionValueSchema
                    elif (
                        issubclass(Entity, Exception)
                        and not issubclass(Entity, Error)
                    ):
                        final_field = ErrorValueSchema
                    elif issubclass(Entity, Error):
                        final_field = ErrorValueSchema
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

        for k, v in self.items:
            final_field: str | dict
            match v:
                case Indicator.TYPE:
                    final_field = self.__get_type_for_object(obj).value
                case Indicator.VALUE:
                    if isinstance(obj, HttpException):
                        final_field = {
                            "status_code": obj.status_code,
                            "message": obj.detail
                        }
                    elif isinstance(obj, RequestValidationException):
                        message: str = ""
                        locations: list[list[str]] = []
                        validation_errors = obj.errors()

                        for err in validation_errors:
                            if err.get("msg", None):
                                # In case of several errors separate their
                                # messages all in one
                                if message:
                                    message += " ;; "
                                message += err["msg"]
                            err_loc: tuple[str | int] = err["loc"]
                            validation.validate_each(
                                err_loc,
                                [str, int],
                                expected_sequence_type=tuple
                            )
                            locations.append(list(validation.apply(
                                err_loc,
                                tuple
                            )))

                        final_field = {
                            "message": message,
                            "locations": locations
                        }
                    elif isinstance(obj, Error):
                        final_field = obj.dict()
                    elif (
                        isinstance(obj, Exception)
                        and not isinstance(obj, Error)
                    ):
                        final_field = {
                            "message": "; ".join([str(x) for x in obj.args])
                        }
                    elif isinstance(obj, Model):
                        # Since pydantic seems to not having a way to deal
                        # with Enums through dict() call (only via Config),
                        # here we do not performance good operation of
                        # converting to json and back to ensure that no Python
                        # objects is remained in digested model.
                        final_field = json.loads(obj.json())
                    else:
                        raise TypeError(
                            f"unsupported obj type {type(obj)}"
                        )
                case _:
                    raise UnsupportedIndicatorError(
                        f"indicator {v} is not supported"
                    )
            result[k] = final_field

        return result

    def recover(
        self,
        Object: type[IndicatableTypeVar],
        mp: dict
    ) -> IndicatableTypeVar:
        """Creates object from given map according to indication rules.

        Note that your project's indication instance should match an indication
        instance used to digest the object.

        Only instances of base classes subclasses can be recovered. E.g.
        Model or Error.

        Recovering of Python's Exception are also supported.

        Args:
            Object:
                Object type to recover.
            mp:
                Dictionary from which object will be recovered.

        Returns:
            Recovered object.

        Raises:
            RecoveringError:
                TYPE or VALUE locations of given dictionary are not matched
                with according indication data.
        """
        validate(Object, type)
        validate_dict(mp, (str, Validator.SKIP))

        # Note that in this case availability of Indicator.TYPE field in given
        # map is not checked since only Indicator.VALUE is needed.
        value: dict = self.__find_value_in_mp(mp)

        if (
            issubclass(Object, HttpException)
        ):
            return Object(
                status_code=value["status_code"],
                detail=value["message"]
            )
        elif (
            issubclass(Object, RequestValidationException)
        ):
            # Temporarily RequestValidationException data is not recovered
            return Object(
                errors=[]
            )
        elif issubclass(Object, Error):
            return Object(message=value["message"])
        elif (
            issubclass(Object, Exception)
        ):
            return Object(*value["message"].split("; "))
        elif issubclass(Object, Model):
            return Object.parse_obj(value)
        else:
            raise TypeError(
                f"unrecognized Object {Object}"
            )

    def __find_value_in_mp(self, mp: dict) -> dict:
        indication_value_field_location: FieldLocation = \
            self.__locations[Indicator.VALUE]
        mp_value: dict = find_field_by_location(
            indication_value_field_location, mp
        )

        validate(mp_value, dict)
        return mp_value

    def __get_type_for_object(
        self,
        obj: Indicatable
    ) -> IndicationType:
        indication_type: IndicationType = IndicationType.OK

        # For models default type is OK, unless is defined
        # otherwise in INDICATION_TYPE
        if isinstance(obj, Model) and obj.INDICATION_TYPE is not None:
            indication_type = validation.apply(
                obj.INDICATION_TYPE,
                IndicationType
            )
        # For Exception indication type is always ERROR, for
        # orwynn.Error it's ERROR by default, unless is
        # defined otherwise in Error.INDICATION_TYPE
        elif isinstance(obj, Exception):
            indication_type = IndicationType.ERROR
            if isinstance(obj, Error) and obj.INDICATION_TYPE is not None:
                indication_type = validation.apply(
                    obj.INDICATION_TYPE,
                    IndicationType
                )

        return indication_type
