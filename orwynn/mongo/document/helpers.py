from typing import Any

from bson import ObjectId

from orwynn.helpers.errors import UnsupportedError


def convert_ids(obj: dict) -> dict:
    """
    Takes an object and converts all string values found there to ids.

    If a nested data containers is found (dictionaries or lists are only
    supported), a recursive convertation for them are performed.
    """
    result: dict = {}

    for k, v in obj:
        new_value: Any
        if type(v) is str:
            new_value = ObjectId(v)
        elif type(v) is dict:
            new_value = convert_ids(v)
        elif type(v) is list:
            new_value = [convert_ids(x) for x in v]
        else:
            raise UnsupportedError(
                title="document id query type",
                value=type(v)
            )

        result[k] = new_value

    return result
