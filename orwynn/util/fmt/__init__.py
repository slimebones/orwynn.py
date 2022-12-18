"""Operations with strings.

Typically here collected functions which return string.
"""
from curses.ascii import isupper
from typing import Any


def format_chain(lst: list[Any]) -> str:
    return " -> ".join([str(x) for x in lst])


def snakefy(name: str) -> str:
    """Converts name to snake_case.

    Args:
        name:
            Name to convert.

    Returns:
        Name converted.
    """
    words: list[str] = []

    word: str = name[0].lower()
    for i, char in enumerate(name[1:]):
        if char.isupper():
            try:
                next_char: str = word[i+1]
            except KeyError:
                words.append(word)
                words.append(char.lower())
            else:
                if next_char.isupper():
                    # Keep continuing uppers
                    word += char
                else:
                    words.append(word)
                    word = char.lower()
        else:
            word += char

    return "_".join(words)


def camelfy(name: str) -> str:
    """Converts name to CamelCase.

    Args:
        name:
            Name to convert.

    Returns:
        Name converted.
    """
    word: str = name[0]

    # The task is typically to convert each letter after underscore to
    # uppercase, but don't touch leading and following underscores
    is_next_uppercase: bool = False
    for char in name[1:]:
        if char == "_":
            is_next_uppercase = True
        elif is_next_uppercase:
            word += char.upper()
            is_next_uppercase = False
        else:
            word += char

    return word
