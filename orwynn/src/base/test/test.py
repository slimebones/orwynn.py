from fastapi import FastAPI
from pytest import fixture
from fastapi.testclient import TestClient

from orwynn.src.app.app_service import AppService
from orwynn.src.base.test.http_client import HttpClient
from orwynn.src.boot.boot import Boot


class Test:
    @fixture
    def http(self, client: TestClient) -> HttpClient:
        return HttpClient(client)

    @fixture
    def app(self) -> AppService:
        # TODO: Initialize Boot here properly or find another solution
        return Boot().app

    @fixture
    def client(self, app: AppService) -> TestClient:
        return app.test_client

    @fixture
    def root_dir(self, app: AppService) -> str:
        return app.root_dir
