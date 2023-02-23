from orwynn.base.error.Error import Error


class DatabaseEntityNotFoundError(Error):
    """When requested database entity is not found."""
    def __init__(
        self,
        message: str = "",
        *,
        collection: str | None = None,
        query: dict | None = None
    ) -> None:
        if not message and collection and query:
            message = \
                f"not found entity for query {query} in collection" \
                + f" {collection}"
        super().__init__(message)
