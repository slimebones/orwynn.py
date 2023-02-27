import pytest

from orwynn.testing import Client


@pytest.fixture
def std_http(std_app) -> Client:
    return std_app.client
