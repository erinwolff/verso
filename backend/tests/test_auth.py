import pytest
from fastapi.testclient import TestClient

from app import auth, config


@pytest.fixture
def client(data_dir, monkeypatch):
    # data_dir points storage at a temp dir; import app after env is set.
    from app.main import app

    return TestClient(app)


def test_auth_disabled_allows_access(client, monkeypatch):
    monkeypatch.setattr(config, "PASSWORD", "")
    r = client.get("/api/auth")
    assert r.json() == {"required": False, "authenticated": True}
    # protected route is reachable with no cookie
    assert client.get("/api/index").status_code == 200


def test_auth_required_blocks_then_allows(client, monkeypatch):
    monkeypatch.setattr(config, "PASSWORD", "open-sesame")

    # blocked without a session
    assert client.get("/api/index").status_code == 401
    state = client.get("/api/auth").json()
    assert state == {"required": True, "authenticated": False}

    # wrong password rejected
    assert client.post("/api/login", json={"password": "nope"}).status_code == 401

    # correct password sets the cookie and unlocks
    r = client.post("/api/login", json={"password": "open-sesame"})
    assert r.status_code == 200
    assert auth.SESSION_COOKIE in r.cookies
    assert client.get("/api/index").status_code == 200

    # logout clears it
    client.post("/api/logout")
    assert client.get("/api/index").status_code == 401


def test_tampered_cookie_rejected(client, monkeypatch):
    monkeypatch.setattr(config, "PASSWORD", "open-sesame")
    client.cookies.set(auth.SESSION_COOKIE, "not-the-real-token")
    assert client.get("/api/index").status_code == 401
