from pathlib import Path
import pytest

@pytest.fixture
def base_preload_dir() -> Path:
    return Path(Path.cwd(), "var/preload")
