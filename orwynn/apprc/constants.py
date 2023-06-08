from orwynn.app import AppMode

# Items with higher index will update resources from lower ones.
APP_RC_MODE_NESTING: list[AppMode] = [
    AppMode.PROD,
    AppMode.DEV,
    AppMode.TEST
]
