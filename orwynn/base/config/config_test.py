from orwynn.base.config.Config import Config
from orwynn.base.config.UnknownConfigSourceError import \
    UnknownConfigSourceError
from orwynn.base.module.Module import Module
from orwynn.boot.Boot import Boot
from orwynn.util.expect import expect


def test_boot_source_on_wrong_config():
    class Cfg(Config):
        SOURCE = "boot"

    expect(
        Boot,
        UnknownConfigSourceError,
        mode="test",
        root_module=Module(route="/m1", Providers=[Cfg])
    )
