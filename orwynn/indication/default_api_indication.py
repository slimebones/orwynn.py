from orwynn.indication.Indication import Indication
from orwynn.indication.Indicator import Indicator

default_api_indication: Indication = Indication(
    {
        "type": Indicator.TYPE,
        "value": Indicator.VALUE
    }
)
