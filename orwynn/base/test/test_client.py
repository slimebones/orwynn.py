from fastapi.testclient import TestClient as NativeTestClient


class TestClient(NativeTestClient):
    pass