from orwynn.base.model.model import Model


class Cors(Model):
    """Represents configuration for special CORS middleware."""
    is_enabled: bool = True
    allow_origins: list[str] | None = None
    allow_origin_regex: str | None = None
    allow_methods: list[str] | None = None
    allow_headers: list[str] | None = None
    allow_credentials: bool = False
    expose_headers: list[str] | None = None
    max_age: int = 600
