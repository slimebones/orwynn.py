from typing import Any

# Location is several nested dicrionary keys joined with ".", e.g. if you have
# dictionary:
# ```python
# {
#     "a1": {
#         "a2": {
#             "a3": 10
#         }
#     }
# }
# ```
# location of field with value 10 will be "a1.a2.a3"
FieldLocation = str


def find_field_location(field: Any, mp: dict) -> FieldLocation:
    """Searches given dictionary to find given field.

    Args:
        field:
            Field value to search.
        mp:
            Dictionary to search in. All keys should be parseable to str.

    Returns:
        Location of field in form "key1.key2.key3" relative to dictionary root.

    Raises:
        ValueError:
            No key with given field found in map.
    """
    key_chain: list[str] = []
    __traverse(field, mp, key_chain)
    key_chain.reverse()
    return ".".join(key_chain)


def __traverse(field: Any, mp: dict, key_chain: list[str]) -> bool:
    # Returns flag signifies whether a key was appended.

    for k, v in mp.items():
        if (
            (
                isinstance(v, dict)
                and __traverse(field, v, key_chain)
            )
            or v == field
        ):
            key_chain.append(str(k))
            return True

    return False
