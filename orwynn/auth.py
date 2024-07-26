from typing import Any, Callable

import jwt
from pydantic import BaseModel
from pykit.check import check
from pykit.log import log
from pykit.res import Ok, Err, Res
from rxcat import Awaitable, sub
from pykit.t import delta

from orwynn import SysArgs, sys
from orwynn.cfg import Cfg
from orwynn.rbac import PermissionDto, PermissionModel


class Login(BaseModel):
    username: str
    password: str

    @staticmethod
    def code():
        return "login"

class Logout(BaseModel):
    auth_token: str

    @staticmethod
    def code():
        return "logout"

class Logged(BaseModel):
    permissions: list[PermissionDto]
    """
    List of initial permissions the logged user have.

    Subject of further change by rbac evts.
    """

    user_sid: str
    user_auth_token: str
    user_auth_token_exp: float

class LoggedOut(BaseModel):
    user_sid: str

    @staticmethod
    def code():
        return "logged_out"

class AuthErr(Exception):
    @staticmethod
    def code():
        return "auth_err"

async def _mock_check_user(req: Login) -> str | None:
    log.warn(
        f"replace dummy check user, received request {req}"
        " => always respond None"
    )
    return None

async def _mock_try_login_user(
    user_sid: str,
    token: str,
    exp: float
) -> list[str] | None:
    log.warn("replace dummy login user => ret None")
    return None

async def _mock_try_logout_user(user_sid: str) -> bool:
    log.warn("replace dummy logout user => ret False")
    return False

class AuthCfg(Cfg):
    check_user_func: Callable[[Login], Awaitable[str | None]] = \
        _mock_check_user
    try_login_user: Callable[
        [str, str, float],
        Awaitable[list[str] | None]
    ] = _mock_try_login_user
    try_logout_user: Callable[[str], Awaitable[bool]] = _mock_try_logout_user

    auth_token_secret: str
    auth_token_algo: str = "HS256"
    auth_token_lifetime: float = 2592000  # 30 days

    class Config:
        arbitrary_types_allowed = True

@sys(AuthCfg)
async def sys__login(args: SysArgs[AuthCfg], body: Login):
    user_sid = await args.cfg.check_user_func(body)

    if not user_sid:
        raise AuthErr("wrong user data")

    token, exp = _encode_jwt(
        user_sid,
        args.cfg.auth_token_secret,
        args.cfg.auth_token_algo,
        args.cfg.auth_token_lifetime)
    permission_codes = await args.cfg.try_login_user(user_sid, token, exp)
    if permission_codes is None:
        raise AuthErr("failed to login user")

    permission_dtos = PermissionModel.to_dtos(
        RbacUtils.get_permissions_by_codes(permission_codes)
    )

    log.info(f"logged user sid {user_sid}", 2)
    return Ok(Logged(
        permissions=permission_dtos,
        user_sid=user_sid,
        user_auth_token=token,
        user_auth_token_exp=exp))


@sys(AuthCfg)
async def sys__logout(args: SysArgs, body: Logout):
    # TODO: for now logout can be made even with old token, need to ensure
    #       user has this token

    # if the token has been expired, logout must not be prohibited
    user_sid = _decode_jwt(
        body.auth_token,
        args.cfg.auth_token_secret,
        args.cfg.auth_token_algo,
        False)
    logout_ok = await args.cfg.try_logout_user(user_sid)
    if not logout_ok:
        return Err(AuthErr(f"logout for user sid {user_sid} failed"))
    log.info(f"logged out user sid {user_sid}", 2)
    return Ok(LoggedOut(user_sid=user_sid))

def _encode_jwt(
        user_sid: str,
        secret: str,
        algo: str,
        lifetime: float) -> tuple[str, float]:
    exp = delta(lifetime)
    token: str = jwt.encode(
        {
            "user_sid": user_sid,
            "exp": exp
        },
        key=secret,
        algorithm=algo)

    return token, exp

def _decode_jwt(
        token: str,
        secret: str,
        algo: str,
        verify_exp: bool = True) -> str:
    try:
        data: dict = jwt.decode(
            token,
            key=secret,
            algorithms=[algo],
            options={
                "verify_exp": verify_exp,
            }
        )
    except jwt.exceptions.ExpiredSignatureError as err:
        raise AuthErr("expired token") from err

    user_sid = data.get("userSid", None)
    check.instance(user_sid, str)
    return user_sid

