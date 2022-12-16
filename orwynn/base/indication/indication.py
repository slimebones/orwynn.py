from typing import Any, ItemsView

from orwynn.base.indication.indicator import Indicator
from orwynn.base.indication.recovering_error import RecoveringError
from orwynn.base.indication.unsupported_indicator_error import \
    UnsupportedIndicatorError
from orwynn.base.model.model import Model
from orwynn.boot.BootDataProxy import BootDataProxy
from orwynn.util.mp.find_field_location import FieldLocation
from orwynn.validation import validate, validate_dict
from orwynn.validation.validator import Validator


__Locations = dict[Indicator, FieldLocation]


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
        validate_dict(mp, (str, Indicator))
        self.__mp: dict[str, Indicator] = mp

        self.__locations_by_supported_class: \
            dict[type, __Locations] = {}
        indicator_type_key_location: str
        indicator_value_key_location: str

    def __find_locations_by_supported_class(
        self
    ) -> dict[type, __Locations]:

        result: dict[type, __Locations]

        for C in self.__SUPPORTED_CLASSES:
            match C:
                case Model:
                    result[Model] =
                case _:
                    raise TypeError(f"unknown supported class {C}")

    def __find_locations_for_model(self) -> __Locations:
        result: __Locations = {}

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

        for k, v in BootDataProxy.ie().api_indication.items:
            final_value: Any
            match v:
                case Indicator.TYPE:
                    final_value = model.__class__.__name__
                case Indicator.VALUE:
                    final_value = model.dict
                case _:
                    raise UnsupportedIndicatorError(
                        f"indicator {v} is not supported in model digesting"
                    )
            result[k] = final_value

        return result

    def recover_model(self, mp: dict, M: type[Model]) -> Model:
        """Creates model object from given map according to indication rules.

        Note that your project's indication instance should match an indication
        instance used to digest the model. Also this indicaiton instance should
        contain Indicator.TYPE and Indicator.VALUE to find and populate model.

        Args:
            mp:
                Dictionary from which model will be recovered.
            M:
                Model class to recover.

        Returns:
            Recovered model.
        """
        validate_dict(mp, (str, Validator.SKIP))

        type_field: str | None = None
        value_field: dict | None = None

        # Find fields representing Indicator.TYPE and Indicator.VALUE. We don't
        # care about other fields for model recovering.
        for mp_k, mp_v in mp.items():
            for indication_k, indication_v \
                    in BootDataProxy.ie().api_indication.items:
                if mp_k == indication_k:
                    match indication_v:
                        case Indicator.TYPE:
                            validate(mp_v, str)
                            type_field = mp_v
                        case Indicator.VALUE:
                            validate(mp_v, dict)
                            value_field = mp_v

        if not type_field:
            raise RecoveringError(
                f"wasn't able to find Indicator.TYPE related field"
            )

    def __find_indicator_key_location(self, key: str) ->
