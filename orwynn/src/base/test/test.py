from fastapi import FastAPI
from pytest import fixture
from fastapi.testclient import TestClient

from src.app.app import App
from src.base.test.http_client import HttpClient


class Test:
    @fixture
    def http(self, client: TestClient) -> HttpClient:
        return HttpClient(client)

    @fixture
    def app(self) -> App:
        return App.ie()

    @fixture
    def client(self, app: App) -> TestClient:
        return app.test_client

    @fixture
    def root_dir(self, app: App) -> str:
        return app.root_dir
