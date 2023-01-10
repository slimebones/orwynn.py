from datetime import datetime, timedelta, timezone

from orwynn import validation


def get_utc_timestamp() -> float:
    return datetime.now(timezone.utc).timestamp()


def get_delta_timestamp(delta: int) -> float:
    """Calculates delta timestamp from current moment adding given delta in
    seconds.
    """
    validation.validate(delta, int)
    return (
        datetime.now(timezone.utc) + timedelta(seconds=delta)
    ).timestamp()
