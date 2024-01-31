from pathlib import Path

import aiohttp

from orwynn.preload import PreloadUdto


def test_preload_1(
    client,
    base_preload_dir: Path
):
    test_file_path = Path(Path.cwd(), "data/share/blueprint1.png")

    formdata = aiohttp.FormData()
    formdata.add_field(
        "files",
        Path.open(test_file_path, "rb")
    )

    data: dict = client.post_jsonify(
        "/preload",
        200,
        data=formdata
    )
    preload_dto = PreloadUdto.model_validate(data)

    assert preload_dto.filenames == ["blueprint1.png"]

    preload_dir = Path(base_preload_dir, preload_dto.sid)
    assert preload_dir.is_dir()
    assert Path(preload_dir, "blueprint1.png").is_file()


def test_preload_2(
    client,
    base_preload_dir: Path
):
    test_file_path_1 = Path(Path.cwd(), "data/share/blueprint1.png")
    test_file_path_2 = Path(Path.cwd(), "data/share/doc1.pdf")

    formdata = aiohttp.FormData()
    formdata.add_field(
        "files",
        Path.open(test_file_path_1, "rb")
    )
    formdata.add_field(
        "files",
        Path.open(test_file_path_2, "rb")
    )

    data: dict = client.post_jsonify(
        "/preload",
        200,
        data=formdata
    )
    preload_dto = PreloadUdto.model_validate(data)

    assert preload_dto.filenames == ["blueprint1.png", "doc1.pdf"]

    preload_dir = Path(base_preload_dir, preload_dto.sid)
    assert preload_dir.is_dir()

    assert Path(preload_dir, "blueprint1.png").is_file()
    assert Path(preload_dir, "doc1.pdf").is_file()

