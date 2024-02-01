from typing import Callable

from rxcat import Req

from orwynn.cfg import Cfg
from orwynn.sys import Sys


class LoginReq(Req):
    username: str
    hashPassword: str

class AuthCfg(Cfg):
    check_user_func: Callable[[LoginReq], bool] = lambda _: False

class AuthSys(Sys[AuthCfg]):
    async def init(self):
        pass

    async def enable(self):
        pass

