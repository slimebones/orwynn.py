import pytest
from orwynn.tst import Client


@pytest.mark.asyncio
async def test_main(client: Client):
    client.get("/admin/codes")

