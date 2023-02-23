from orwynn.base.model.Model import Model


class Cors(Model):
    """Represents configuration for special CORS middleware."""
    allow_origins: list[str] | None = None
    allow_origin_regex: list[str] | None = None
    allow_methods: list[str] | None = None
    allow_headers: list[str] | None = None
    allow_credentials: bool = False
    expose_headers: list[str] | None = None
    max_age: int = 600
