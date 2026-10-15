import httpx
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_index_serves_page():
    resp = client.get("/")
    assert resp.status_code == 200
    assert "调用后端" in resp.text


def test_ask_forwards_to_backend(monkeypatch):
    captured = {}

    def fake_post(url, json=None, timeout=None):
        captured["url"] = url
        captured["json"] = json
        return FakeResponse({"message": "Hello, tom!", "from": "backend"})

    monkeypatch.setattr(httpx, "post", fake_post)
    resp = client.get("/ask?name=tom")
    assert resp.status_code == 200
    assert resp.json() == {"message": "Hello, tom!", "from": "backend"}
    assert captured["url"].endswith("/api/greet")
    assert captured["json"] == {"name": "tom", "times": 1}


def test_ask_backend_down(monkeypatch):
    def boom(url, json=None, timeout=None):
        raise httpx.ConnectError("cannot connect")

    monkeypatch.setattr(httpx, "post", boom)
    resp = client.get("/ask")
    assert resp.status_code == 200
    assert resp.json()["message"] == "backend service unavailable"
