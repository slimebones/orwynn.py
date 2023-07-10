from enum import Enum


class CliCommand(Enum):
    """
    Main command that can be given as a first argument for CLI.

    Attributes:
        Test:
            Run application in test mode.
        Dev:
            Run application in dev mode.
        Prod:
            Run application in prod mode.
    """
    Test = "test"
    Dev = "dev"
    Prod = "prod"
