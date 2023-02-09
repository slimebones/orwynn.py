import uuid


def gen_uuid() -> str:
    """Creates unique id.

    Returns:
        Id created.
    """
    return uuid.uuid4().hex
