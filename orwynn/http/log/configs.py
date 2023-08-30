from orwynn.base.config.config import Config


class LogHttpMiddlewareConfig(Config):
    is_request_logged: bool = False
    is_response_logged: bool = False
