from typing import Callable

from .client import Client
from .embeddedclient import EmbeddedTestClient


def get_log_apprc(check_fn: Callable) -> dict:
    return {
        "prod": {
            "Log": {
                "handlers": [
                    {
                        "sink": check_fn,
                        "serialize": True
                    }
                ]
            },
            "LogHttpMiddleware": {
                "is_request_logged": True,
                "is_reposne_logged": True
            }
        }
    }


class Writer:
    # NOTE: Try adding "await Log.complete()" if log handlers have no time to
    #   process messages before calling Writer.read().
    def __init__(self):
        self._output = ""

    def write(self, message):
        self._output += message

    def read(self):
        return self._output
