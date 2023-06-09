from orwynn.base import Config
from orwynn.http.cors.cors import Cors


class AppConfig(Config):
    docs_route: str = "/docs"
    redoc_route: str = "/redoc"
    cors: Cors | None = None
