from pathlib import Path


def test_preload_1(
    client: Client,
    root_dir: Path,
    base_preload_dir: Path
):
    test_file_path = Path(root_dir, "data/share/blueprint1.png")
    data: dict = client.post_jsonify(
        "/preload",
        200,
        files=[("files", Path.open(test_file_path, "rb"))]
    )
    preload_dto = PreloadUdto.recover(data)

    assert preload_dto.filenames == ["blueprint1.png"]

    preload_dir = Path(base_preload_dir, preload_dto.sid)
    assert preload_dir.is_dir()
    assert Path(preload_dir, "blueprint1.png").is_file()


def test_preload_2(
    client: Client,
    root_dir: Path,
    base_preload_dir: Path
):
    test_file_path_1 = Path(root_dir, "data/share/blueprint1.png")
    test_file_path_2 = Path(root_dir, "data/share/doc1.pdf")
    data: dict = client.post_jsonify(
        "/preload",
        200,
        files=[
            ("files", Path.open(test_file_path_1, "rb")),
            ("files", Path.open(test_file_path_2, "rb"))
        ]
    )
    preload_dto = PreloadUdto.recover(data)

    assert preload_dto.filenames == ["blueprint1.png", "doc1.pdf"]

    preload_dir = Path(base_preload_dir, preload_dto.sid)
    assert preload_dir.is_dir()

    assert Path(preload_dir, "blueprint1.png").is_file()
    assert Path(preload_dir, "doc1.pdf").is_file()

