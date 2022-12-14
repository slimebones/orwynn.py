from orwynn.boot.boot_mode import BootMode


class BOOT_CONFIG_PROXY_DATA:
    """Proxy data to avoid circular imports between Boot, BootConfig and DI"""
    root_dir: str
    mode: BootMode
