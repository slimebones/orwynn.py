from typing import Any, ItemsView
from orwynn.base.indication.indicator import Indicator
from orwynn.base.indication.unsupported_indicator_error import UnsupportedIndicatorError
from orwynn.base.model.model import Model
from orwynn.boot.BootDataProxy import BootDataProxy
from orwynn.validation import validate_dict


class Indication:
    """Holds some representation of how the data should be built like to serve
    as an convention for building objects.

    Each indication is simply mapping between strings and Indicators, but also
    implements special digest_* methods to transform given object applying
    defined indication rules.

    Strings-only as keys are used for an additional constraints for objects
    building an API structures, in future it is possible to see here an
    additional flags controlling this behaviour.

    For the list of applicable types see Indicator.
    """

    def __init__(self, mp: dict[str, Indicator]) -> None:
        validate_dict(mp, (str, Indicator))
        self.__mp: dict[str, Indicator] = mp

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
