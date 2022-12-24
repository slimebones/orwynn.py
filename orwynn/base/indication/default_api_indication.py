from orwynn.base.indication.Indication import Indication
from orwynn.base.indication.Indicator import Indicator


default_api_indication: Indication = Indication(
    {
        "type": Indicator.TYPE,
        "value": Indicator.VALUE
    }
)
