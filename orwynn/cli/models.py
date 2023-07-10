from orwynn.base.model.model import Model
from orwynn.cli.enums import CliCommand


class CliCommandData(Model):
    """
    Data required for the chosen mode.

    @abstract
    """


class RunCliCommandData(CliCommandData):
    """
    Data sufficient for modes: Test, Dev and Prod.
    """
    host: str
    port: int


class CliArgs(Model):
    command: CliCommand
    data: CliCommandData
