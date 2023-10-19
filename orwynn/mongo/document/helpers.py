
from bson import ObjectId
from bson.errors import InvalidId

from orwynn.mongo.document.errors import InvalidIdError
from orwynn.utils.types import T


def convert_to_object_id(obj: T) -> T | ObjectId:
    """
    Converts an object to ObjectId compliant.

    If the object is:
    - string: It is passed directly to ObjectId()
    - dict: All values are recursively converted using this method.
    - list: All items are recursively converted using this method.
    - other types: Nothing will be done.

    Returns:
        ObjectId-compliant representation of the given object.
    """
    result: T | ObjectId

    if type(obj) is str:
        try:
            result = ObjectId(obj)
        except InvalidId as error:
            raise InvalidIdError(
                invalid_id=obj
            ) from error
    elif type(obj) is dict:
        result = type(obj)()
        for k, v in obj.items():
            result[k] = convert_to_object_id(v)
    elif type(obj) is list:
        result = type(obj)([convert_to_object_id(x) for x in obj])
    else:
        result = obj

    return result
