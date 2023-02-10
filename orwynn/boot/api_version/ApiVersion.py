from typing import Optional
from orwynn.model.Model import Model


class ApiVersion(Model):
    """Describes project's API versioning rules.

    Attributes:
        supported (optional):
            Set of version numbers supported. Defaults to only one supported
            version v1.
    """
    supported: Optional[set[int]] = None
