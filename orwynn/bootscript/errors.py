class NoScriptsForCallTimeError(Exception):
    """
    When no bootscripts are added for certain call time.
    """


class ScriptsAlreadyCalledError(Exception):
    """
    If some scripts were already called.
    """
