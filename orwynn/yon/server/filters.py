from yon.server import Bus

__all__ = [
    "disable_subfn_lsid"
]


def disable_subfn_lsid(_):
    Bus.ie().set_ctx_subfn_lsid(None)
