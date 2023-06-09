from copy import deepcopy
from typing import Any

import dictdiffer

from orwynn.utils import validation
from orwynn.utils.mp.dictpp import dictpp


def find(location: str, mp: dict) -> Any:
    """Finds field by location.

    Args:
        location:
            String representing location to search from in format
            "key1.key2.key3".
        mp:
            Dict to search in.

    Returns:
        Field found.
    """
    validation.validate(location, str)
    validation.validate(mp, dict)

    return dictpp(mp)[location]


def patch(
    to_be_patched: dict,
    source: dict,
    should_deepcopy: bool = True
) -> dict:
    """Patch one dictionary by another.

    Args:
        to_be_patched:
            Dict to be patched.
        source:
            Source dict to use for patching.
        should_deepcopy (optional):
            Whether deepcopy() should be performed on patched dict. Defaults
            to True. If False is passed, it is convenient to not accept
            returned dict since it is the same as passed one to patch.

    Returns:
        Patched dictionary.
    """
    validation.validate(to_be_patched, dict)
    validation.validate(source, dict)

    patched: dictpp

    # Cast to dictpp to operation with locations. At return it's important
    # to cast it back to normal dict.
    patched = dictpp(
        deepcopy(to_be_patched) if should_deepcopy else to_be_patched
    )

    diff = dictdiffer.diff(to_be_patched, source)

    event_name: str
    location: str
    change: Any

    for event in diff:
        # Unpack event tuple
        event_name, location, change = event
        # How dictdiffer event_name, location and change would like for a
        # reference:
        #   change BurgerShot.menu.cola (1.5, 1.8)
        #   add BurgerShot.menu [('pizza', 4.1), ('fried_chicken', 3.5)]

        # Consider only adding and changing events
        if event_name == "add":
            final_location: str
            for addition in change:
                # Calculate final location in patched dict
                final_location = ".".join(
                    [location, addition[0]]
                ) if location else addition[0]
                patched[final_location] = addition[1]

        elif event_name == "change":
            if location == "":
                raise ValueError(
                    "on change events location shouldn't be empty"
                )
            patched[location] = change[1]

    # Cast back to normal dictionary
    return dict(patched)
