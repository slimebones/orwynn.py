"""Operations with strings.

Typically here collected functions which return string.
"""
from typing import Any


def format_chain(lst: list[Any]) -> str:
    return " -> ".join([str(x) for x in lst])


def snakefy(name: str) -> str:
    """Convert given camel-case name to snake case.

    Args:
        name:
            Name to convert.

    Returns:
        Name converted to snake_case.
    """
    words = []

    word = name[0].lower()
    for char in name[1:]:
        if char.isupper():
            words.append(word)
            word = char.lower()
        else:
            word += char.lower()
    words.append(word)

    return "_".join(words)
