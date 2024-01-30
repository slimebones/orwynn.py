import argparse
import sys

from orwynn.cli.enums import CliCommand
from orwynn.cli.models import CliArgs, CliCommandData, RunCliCommandData


class Cli:
    """
    Manages incoming CLI input and calls appropriate Orwynn commands.
    """
    def execute(
        self,
        args: list[str] | None = None
    ) -> None:
        """
        Executes arguments as a commands to Orwynn.

        Args:
            args(optional):
                List of arguments splitted by space. Defaults to system input.
        """


    def _parse_args(
        self,
        args: list[str] | None = None
    ) -> CliArgs:
        arg_list: list[str]
        if args:
            arg_list = args
        else:
            arg_list = sys.argv

        # TODO(ryzhovalex): ensure call like "python -m ..." does not broke
        #   this
        # 0
        command: CliCommand = CliCommand(arg_list[2])

        return CliArgs(
            command=command,
            data=self._get_cli_command_data(
                command,
                arg_list[3:]
            )
        )

    def _get_cli_command_data(
        self,
        command: CliCommand,
        data_args: list[str]
    ) -> CliCommandData:
        data: CliCommandData
        namespace: argparse.Namespace
        parser: argparse.ArgumentParser = argparse.ArgumentParser(
            description=f"Orwynn {command.value.capitalize()} CLI"
        )

        match command:
            case CliCommand.Test:
                raise NotImplementedError
            case CliCommand.Dev:
                self._add_dev_args(parser)
                namespace = parser.parse_args(data_args)
                host, port =
                data = RunCliCommandData(
                    host=namespace.
                )
            case CliCommand.Prod:
                self._add_prod_args(parser)


        return data

    def _add_dev_args(self, parser: argparse.ArgumentParser) -> None:
        self._add_run_args(parser)

    def _add_prod_args(self, parser: argparse.ArgumentParser) -> None:
        self._add_run_args(parser)

    def _add_run_args(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "address",
            type=str,
            help="address to serve on in format 'host:port'"
        )
