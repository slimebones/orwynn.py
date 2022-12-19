from pathlib import Path

from pytest import fixture
from orwynn.base.indication.default_api_indication import \
    default_api_indication
from orwynn.boot.BootMode import BootMode
from orwynn.boot.BootDataProxy import BootDataProxy


@fixture
def std_boot_data_proxy() -> BootDataProxy:
    return BootDataProxy(
        root_dir=Path.cwd(),
        mode=BootMode.TEST,
        api_indication=default_api_indication,
        app_rc={}
    )
