import uuid


def makeid() -> str:
    """Creates unique id.

    Returns:
        Id created.
    """
    return uuid.uuid4().hex
