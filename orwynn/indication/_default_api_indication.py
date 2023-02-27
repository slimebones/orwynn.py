from orwynn.indication._Indication import Indication
from orwynn.indication._Indicator import Indicator

default_api_indication: Indication = Indication(
    {
        "type": Indicator.TYPE,
        "value": Indicator.VALUE
    }
)
