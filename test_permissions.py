
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_admin_only_users_endpoint_rejects_missing_token():
    response = client.get("/api/v1/users")
    assert response.status_code == 401


def test_login_rejects_invalid_credentials():
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "not_a_real_user",
            "password": "Incorrect-Password-2026!",
        },
    )
    assert response.status_code == 401
