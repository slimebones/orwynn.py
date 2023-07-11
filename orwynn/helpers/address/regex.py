ADDRESS_REGEX: str = r"(?P<protocol>\w+\:\/\/)?(?P<userinfo>(?P<username>[a-z0-9]+)\:(?P<password>[a-z0-9]*)\@)?(?P<host>[a-z0-9_\-\.]+)(?:\:(?P<port>\d+))?(?P<path>\/[^\?\s\#]*)?(?:\?(?P<query>[^\#\s]*))?(?:\#(?P<fragment>.+))?"  # noqa: E501

IP_HOST_REGEX: str = r"(?P<ip>[0-9\.]+)"
DOMAIN_HOST_REGEX: str = r"(?P<subdomain>[a-z0-9_\-]+\.)?(?P<seconddomain>[a-z0-9_\-]+\.)?(?P<topdomain>[a-z0-9_\-]+)"  # noqa: E501
