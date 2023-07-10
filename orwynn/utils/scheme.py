from enum import Enum


class Scheme(Enum):
    """
    Supported URI schemes.
    """
    HTTP = "http"
    HTTPS = "https"
    WEBSOCKET = "websocket"
    RTSP = "rtsp"
