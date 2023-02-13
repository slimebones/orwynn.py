from typing import Callable


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
            }
        }
    }
