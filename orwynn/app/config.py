from orwynn.base import Config


class AppConfig(Config):
    docs_route: str = "/docs"
    redoc_route: str = "/redoc"
