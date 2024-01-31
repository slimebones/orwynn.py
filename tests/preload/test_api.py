from pathlib import Path
import aiohttp
import pytest
from orwynn.preload import PreloadUdto

@pytest.mark.asyncio
async def test_preload_1(
    client,
    base_preload_dir: Path
):
    test_file_path = Path(Path.cwd(), "assets/sample.jpg")

    formdata = aiohttp.FormData()
    formdata.add_field(
        "files",
        Path.open(test_file_path, "rb")
    )

    data: dict = await client.post_jsonify(
        "/preload",
        200,
        data=formdata
    )
    preload_dto = PreloadUdto.model_validate(data)

    assert preload_dto.filenames == ["sample.jpg"]

    preload_dir = Path(base_preload_dir, preload_dto.sid)
    assert preload_dir.is_dir()
    assert Path(preload_dir, "sample.jpg").is_file()

@pytest.mark.asyncio
async def test_preload_2(
    client,
    base_preload_dir: Path
):
    test_file_path_1 = Path(Path.cwd(), "assets/sample.jpg")
    test_file_path_2 = Path(Path.cwd(), "assets/sample.pdf")

    formdata = aiohttp.FormData()
    formdata.add_field(
        "files",
        Path.open(test_file_path_1, "rb")
    )
    formdata.add_field(
        "files",
        Path.open(test_file_path_2, "rb")
    )

    data: dict = await client.post_jsonify(
        "/preload",
        200,
        data=formdata
    )
    preload_dto = PreloadUdto.model_validate(data)

    assert preload_dto.filenames == ["sample.jpg", "sample.pdf"]

    preload_dir = Path(base_preload_dir, preload_dto.sid)
    assert preload_dir.is_dir()

    assert Path(preload_dir, "sample.jpg").is_file()
    assert Path(preload_dir, "sample.pdf").is_file()

