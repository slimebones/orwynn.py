from datetime import datetime, timedelta, timezone

from orwynn.utils import validation
from orwynn.utils.types import Delta, Timestamp


def get_utc_timestamp() -> Timestamp:
    return datetime.now(timezone.utc).timestamp()


def get_delta_timestamp(delta: Delta) -> Timestamp:
    """Calculates delta timestamp from current moment adding given delta in
    seconds.
    """
    validation.validate(delta, Delta)
    return (
        datetime.now(timezone.utc) + timedelta(seconds=delta)
    ).timestamp()
