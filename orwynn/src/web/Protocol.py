from enum import Enum


class Protocol(Enum):
    """
    Supported protocols.
    """
    HTTP = "http"
    WEBSOCKET = "websocket"
