from orwynn.base.error._Error import Error


class ProviderKeywordAttributeError(Error):
    """Providers cannot have keyword-only attributes, it's not logical for DI.
    """
    pass
