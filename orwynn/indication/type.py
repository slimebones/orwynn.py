from enum import Enum


class IndicationType(Enum):
    """Possible values of field "type".

    Values:
        OK:
            Everything is correct.
        ERROR:
            Some error is happened either by client's problem or by server's
            issue. Here goes also all errors connected with business-logic
            itself.
    """
    OK = "ok"
    # FIXME: In future, consider moving all non-BL related problems
    # to another type, e.g. "http-error".
    ERROR = "error"
