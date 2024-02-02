from typing import Callable

from fcode import code
from pykit.log import log
from rxcat import Awaitable, Evt, Req

from orwynn.cfg import Cfg
from orwynn.rbac import PermissionDto
from orwynn.sys import Sys


@code("orwynn.login-req")
class LoginReq(Req):
    username: str
    hashPassword: str

@code("orwynn.logout-req")
class LogoutReq(Req):
    authToken: str

@code("orwynn.logged-evt")
class LoggedEvt(Evt):
    permissions: list[PermissionDto]
    """
    List of initial permissions the logged user have.

    Subject of further change by rbac evts.
    """

@code("orwynn.logout-evt")
class LogoutEvt(Evt):
    pass

async def _dummy_check_user(req: LoginReq) -> bool:
    log.warn(
        f"replace dummy check user, received request {req}"
        " => always respond false"
    )
    return False

class AuthCfg(Cfg):
    check_user_func: Callable[[LoginReq], Awaitable[bool]] = _dummy_check_user

class AuthSys(Sys[AuthCfg]):
    async def init(self):
        pass

    async def enable(self):
        await self._sub(LoginReq, self._on_login_req)

    async def _on_login_req(self, req: LoginReq):
        check_result = await self._cfg.check_user_func(req)

        # todo: tmp always return positive
        permissions = [
            PermissionDto(
                code="orwynn-test.test-permission",
                name="Test permission",
                dscr="I'm just a test, don't hurt me."
            )
        ]
        evt = LoggedEvt(rsid=req.msid, permissions=permissions)
        await self._pub(evt)

    async def _on_logout_req(self, req: LogoutReq):
        await self._pub(LogoutEvt(rsid=req.msid))

