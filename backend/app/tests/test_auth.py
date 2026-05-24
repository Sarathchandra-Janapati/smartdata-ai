import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Patch DB dependencies before importing app
with patch("app.database.mysql_db.engine"), \
     patch("app.database.mysql_db.init_mysql"):
    from app.main import app

client = TestClient(app, raise_server_exceptions=False)


def _mock_user(username="testuser", email="test@test.com", role="user"):
    user = MagicMock()
    user.username = username
    user.email = email
    user.role = role
    user.password = "$2b$12$KIXeATz6LRqp5s.iZDJp4.3VQVCd5rAdCBzIOVnhGJhJgr0IZlWNe"  # "password123"
    return user


def test_root():
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200


def test_register_success():
    with patch("app.api.routes.auth_routes.get_user_by_username", return_value=None), \
         patch("app.api.routes.auth_routes.get_user_by_email", return_value=None), \
         patch("app.api.routes.auth_routes.create_user", return_value=_mock_user()):
        resp = client.post("/api/auth/register", json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
            "role": "user",
        })
        assert resp.status_code == 201
        assert "username" in resp.json()


def test_register_duplicate_username():
    with patch("app.api.routes.auth_routes.get_user_by_username", return_value=_mock_user()):
        resp = client.post("/api/auth/register", json={
            "username": "testuser",
            "email": "new@example.com",
            "password": "password123",
            "role": "user",
        })
        assert resp.status_code == 409


def test_login_invalid_credentials():
    with patch("app.api.routes.auth_routes.get_user_by_username", return_value=None):
        resp = client.post("/api/auth/login", data={"username": "nobody", "password": "wrong"})
        assert resp.status_code == 401


def test_profile_unauthenticated():
    resp = client.get("/api/auth/profile")
    assert resp.status_code == 401
