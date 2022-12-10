from typing import Any


def format_chain(l: list[Any]) -> str:
    return " -> ".join([str(x) for x in l])