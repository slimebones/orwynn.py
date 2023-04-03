"""Cryptographic operations.

For password hashing uses bcrypt, which has the salt saved into the hash
itself.

See password hashing https://stackoverflow.com/a/23768422/14748231
"""
import bcrypt

from orwynn.utils import validation


def hash_password(plain_password: str, encoding: str = "utf-8") -> str:
    validation.validate(plain_password, str)
    validation.validate(encoding, str)

    return bcrypt.hashpw(
        plain_password.encode(encoding),
        bcrypt.gensalt()
    ).decode(encoding)


def check_password(
    plain_password: str,
    hashed_password: str,
    encoding: str = "utf-8"
) -> bool:
    validation.validate(plain_password, str)
    validation.validate(hashed_password, str)
    validation.validate(encoding, str)

    return bcrypt.checkpw(
        plain_password.encode(encoding),
        hashed_password.encode(encoding)
    )
