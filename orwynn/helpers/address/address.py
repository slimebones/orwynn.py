from typing import Self

from orwynn.base.model.model import Model
from orwynn.utils.scheme import Scheme


class Address(Model):
    """
    Representation of URL.

    Attributes:
        host:
            Host of the address.
        top_domain(optional):
            Top-level domain. Defaults to host name in case of ip-like
            hostname (such as `127.0.0.1`).
        second_domain(optional):
            Second-level domain. Defaults to None.
        subdomain(optional):
            Subdomain. Defaults to None.
        port(optional):
            Port of the address. Defaults to None.
        protocol(optional):
            Protocol of the address. Defaults to None.
        path(optional):
            Route of the address. Defaults to None.
        query(optional):
            Query arguments of the address. Query's values are not converted
            to basic types, all of them are strings or list of strings - for
            multiple occured keys, all occured values are added to the list
            for the key. Defaults to None.
        username(optional):
            Username of the address. Defaults to None.
        password(optional):
            Password of the address. Defaults to None.
        fragment(optional):
            Fragment of the address. Defaults to None.
    """
    host: str
    top_domain: str | None = None
    second_domain: str | None = None
    subdomain: str | None = None
    scheme: Scheme | None = None
    port: int | None = None
    path: str | None = None
    query: dict[str, str | list[str]] | None = None
    username: str | None = None
    password: str | None = None
    fragment: str | None = None

    @classmethod
    def parse(cls, raw_address: str) -> Self:
        """
        Parses a raw address into the model.

        Args:
            raw_address:
                Address to parse.

        Returns:
            Address model.

        Raises:
            InvalidAddressError:
                The given raw address does not match address's regex.
        """
        raise NotImplementedError()
