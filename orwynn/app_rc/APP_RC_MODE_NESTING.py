from orwynn.boot.BootMode import BootMode


# Items with higher index will update resources from lower ones.
APP_RC_MODE_NESTING: list[BootMode] = [
    BootMode.PROD,
    BootMode.DEV,
    BootMode.TEST
]
