from typing import Any, ItemsView
from orwynn.base.indication.digesting_error import DigestingError

from orwynn.base.indication.indicator import Indicator
from orwynn.base.indication.recovering_error import RecoveringError
from orwynn.base.indication.unsupported_indicator_error import \
    UnsupportedIndicatorError
from orwynn.base.model.model import Model
from orwynn.util.cls import find_subclass_by_name
from orwynn.util.mp.location import FieldLocation, find_field_by_location, find_location_by_field
from orwynn.util.validation import validate_dict
from orwynn.util.validation.validator import Validator


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
    __SUPPORTED_CLASSES: list[type] = [
        Model
    ]

    def __init__(self, mp: dict[str, Indicator]) -> None:
        validate_dict(mp, (str, Validator.SKIP))  # bad support for Enums
        self.__mp: dict[str, Indicator] = mp

        self.__locations_by_supported_class: \
            dict[type, _Locations] = \
                self.__find_locations_by_supported_class()

    def __find_locations_by_supported_class(
        self
    ) -> dict[type, _Locations]:

        result: dict[type, _Locations] = {}

        for C in self.__SUPPORTED_CLASSES:
            if C is Model:
                result[Model] = self.__find_locations_for_model()
            else:
                raise TypeError(f"no logic to handle class {C}")

        return result

    def __find_locations_for_model(self) -> _Locations:
        return {
            Indicator.TYPE: find_location_by_field(Indicator.TYPE, self.__mp),
            Indicator.VALUE: find_location_by_field(Indicator.VALUE, self.__mp)
        }

    @property
    def items(self) -> ItemsView[str, Indicator]:
        return self.__mp.items()

    def digest_model(self, model: Model) -> dict:
        """Traverses the given model to create dictionary based on defined
        indicators.

        Args:
            model:
                Model to be digested.

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
            final_value: Any
            match v:
                case Indicator.TYPE:
                    final_value = model.__class__.__name__
                    is_type_indicator_found = True
                case Indicator.VALUE:
                    final_value = model.dict
                    is_value_indicator_found = True
                case _:
                    raise UnsupportedIndicatorError(
                        f"indicator {v} is not supported in model digesting"
                    )
            result[k] = final_value

        if not is_type_indicator_found:
            raise DigestingError(
                f"indication {self} should contain indicator {Indicator.TYPE}"
                f" and {Indicator.VALUE} in any fields to be able to digest"
                " models"
            )

        if not is_value_indicator_found:
            raise DigestingError(
                f"wasn't able to find Indicator.VALUE related field"
            )

        return result

    def recover_model(self, mp: dict) -> Model:
        """Creates model object from given map according to indication rules.

        Note that your project's indication instance should match an indication
        instance used to digest the model. Also this indicaiton instance should
        contain Indicator.TYPE and Indicator.VALUE to find and populate model.

        Args:
            mp:
                Dictionary from which model will be recovered.

        Returns:
            Recovered model.

        Raises:
            RecoveringError:
                TYPE or VALUE locations of given dictionary are not matched
                with according indication data.
        """
        validate_dict(mp, (str, Validator.SKIP))

        TargetModel: type[Model] = self.__find_model_type_in_mp(mp)

    def __find_model_type_in_mp(self, mp: dict) -> type[Model]:
        indication_type_field_location: FieldLocation = \
            self.__locations_by_supported_class[Model][Indicator.TYPE]
        mp_type_field: str = find_field_by_location(
            indication_type_field_location, mp
        )
        return find_subclass_by_name(mp_type_field, Model)

    def __find_model_value_in_mp(self, mp: dict) -> dict:
        indication_value_field_location: FieldLocation = \
            self.__locations_by_supported_class[Model][Indicator.VALUE]
        mp_value_field_location: FieldLocation = find_location_by_field(
            Indicator.VALUE, mp
        )
        if indication_value_field_location != mp_type_field_location:
            raise RecoveringError(
                "indication value field location"
                f" {indication_value_field_location} is not matched with"
                " given map value field location"
                f" {mp_value_field_location}"
            )
