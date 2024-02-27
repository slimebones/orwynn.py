import pytest

from orwynn.tst import Client


@pytest.mark.asyncio
async def test_main(client: Client):
    res = await client.get(
        "/admin/codes",
        headers={
            "Origin": "http://test.example.com"
        }
    )
    assert \
        set(res.headers["Access-Control-Expose-Headers"].split(",")) \
            == set("Server,Date,Content-Length".split(","))
    assert \
        res.headers["Access-Control-Allow-Origin"] \
            == "http://test.example.com"
    assert \
        res.headers["Access-Control-Allow-Credentials"] \
            == "true"

