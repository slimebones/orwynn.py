from enum import Enum


class ServerEngine(Enum):
    """
    The server used under the hood.

    Attributes:
        Uvicorn:
            ASGI web server implementation for Python.
    """
    Uvicorn = "uvicorn"
