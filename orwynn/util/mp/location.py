from typing import Any

# Location is several nested dicrionary keys joined with ".", e.g. if you have
# dictionary:
# ```python
# ```
# location of field with value 10 will be "a1.a2.a3"
FieldLocation = str


class FieldNotFoundError(Exception):
    pass


class MalformedLocationError(Exception):
    pass


def find_location_by_field(field: Any, mp: dict) -> FieldLocation:
    """Searches given dictionary to find given field.

    Args:
        field:
            Field value to search.
        mp:
            Dictionary to search in. All keys should be parseable to str.

    Returns:
        Location of field in form "key1.key2.key3" relative to dictionary root.

    Raises:
        FieldNotFoundError:
            No key with given field found in map.
    """
    key_chain: list[str] = []

    is_found: bool = __traverse_comparing_field(field, mp, key_chain)

    if not is_found:
        raise FieldNotFoundError(
            f"no key with field {field} in given map {mp}"
        )

    key_chain.reverse()
    return ".".join(key_chain)


def find_field_by_location(location: FieldLocation, mp: dict) -> Any:
    """Searches given map to find location and extract field.

    Args:
        location:
            What search for.
        mp:
            What to search in.

    Returns:
        Field value found.
    """
    result: Any = mp
    keys: list[str] = __get_location_keys(location)
    keys.reverse()

    while keys:
        try:
            result = result[keys.pop()]
        except KeyError as err:
            raise FieldNotFoundError(
                f"no field for location \"{location}\" in map {mp}"
            ) from err

    return result


def __get_location_keys(location: FieldLocation) -> list[str]:
    if location == "":
        raise MalformedLocationError("empty location given")

    keys: list[str] = location.split(".")

    if keys == []:
        raise MalformedLocationError(
            f"malformed location {location}"
        )

    return keys


def __traverse_comparing_field(
    field: Any,
    mp: dict,
    key_chain: list[str]
) -> bool:
    # Returns flag signifies whether a key was appended.

    for k, v in mp.items():
        if (
            (
                isinstance(v, dict)
                and __traverse_comparing_field(field, v, key_chain)
            )
            or v == field
        ):
            key_chain.append(str(k))
            return True

    return False
