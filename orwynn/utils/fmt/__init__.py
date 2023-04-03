"""Operations with strings.

Typically here collected functions which return string.
"""
import re
from typing import Any


def format_chain(lst: list[Any]) -> str:
    return " -> ".join([str(x) for x in lst])


def kebabify(name: str) -> str:
    """Converts name to kebab-case.

    Args:
        name:
            Name to convert.

    Returns:
        Name converted.
    """
    # All underscores are simply replaced
    return name.lower().replace("_", "-")


def snakefy(name: str) -> str:
    """Converts name to snake_case.

    Note that this is not reversible using camelfy().

    Args:
        name:
            Name to convert.

    Returns:
        Name converted.
    """
    # Reference: https://stackoverflow.com/a/1176023/14748231
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    name = re.sub("__([A-Z])", r"_\1", name)
    name = re.sub("([a-z0-9])([A-Z])", r"\1_\2", name)
    return name.lower()


def pascalify(name: str) -> str:
    """Converts name to PascalCase.

    Args:
        name:
            Name to convert.

    Returns:
        Name converted.
    """
    result: str = ""
    is_previous_underscore: bool = True

    for i, char in enumerate(name):
        if is_previous_underscore:
            if char == "_":
                result += char
            else:
                result += char.upper()
        else:
            if char != "_":
                result += char
            else:
                try:
                    next_char: str = name[i + 1]
                except IndexError:
                    result += char
                else:
                    if next_char == "_":
                        result += char
        is_previous_underscore = char == "_"

    return result
