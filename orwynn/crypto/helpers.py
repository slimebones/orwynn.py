import bcrypt

from orwynn import validation


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
