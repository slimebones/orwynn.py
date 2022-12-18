import io
import re
from contextlib import redirect_stdout
from typing import Callable

from orwynn.log.bootlog.Bootlog import Bootlog

_MESSAGE: str = "hello world!"
_LOG_MATCH_PATTERN: str = \
    r"\d{4}-\d\d-\d\d at \d\d:\d\d:\d\d\.\d{6}\+\d{4}" \
    + r" - \[Boot \/ .+(DEBUG|INFO|WARNING|ERROR|CRITICAL).+\] .+"


def _get_stdout(fn: Callable, *args, **kwargs) -> str:
    stringio = io.StringIO()
    with redirect_stdout(stringio):
        fn(*args, **kwargs)
    return stringio.getvalue()


def test_debug():
    assert \
        re.match(_LOG_MATCH_PATTERN, _get_stdout(Bootlog.debug, _MESSAGE)) \
        is not None


def test_info():
    assert \
        re.match(_LOG_MATCH_PATTERN, _get_stdout(Bootlog.info, _MESSAGE)) \
        is not None


def test_warning():
    assert \
        re.match(_LOG_MATCH_PATTERN, _get_stdout(Bootlog.warning, _MESSAGE)) \
        is not None


def test_error():
    assert \
        re.match(_LOG_MATCH_PATTERN, _get_stdout(Bootlog.error, _MESSAGE)) \
        is not None


def test_critical():
    assert \
        re.match(_LOG_MATCH_PATTERN, _get_stdout(Bootlog.critical, _MESSAGE)) \
        is not None
