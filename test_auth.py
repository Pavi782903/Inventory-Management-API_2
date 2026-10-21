
import os
import uuid

import pytest
from fastapi.testclient import TestClient

# Set TEST_DATABASE_URL before importing the app in a fully
# isolated test setup. Do not point tests at production data.
from app.main import app

client = TestClient(app)


@pytest.mark.skipif(
    not os.getenv("RUN_API_INTEGRATION_TESTS"),
    reason="Set RUN_API_INTEGRATION_TESTS=1 to run API integration tests",
)
def test_register_login_and_profile():
    suffix = uuid.uuid4().hex[:12]
    username = f"user_{suffix}"
    email = f"{suffix}@example.com"
    password = "Secure-Test-Password-2026!"

    registered = client.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password,
        },
    )
    assert registered.status_code == 201
    body = registered.json()
    assert body["role"] == "Employee"
    assert "hashed_password" not in body

    duplicate = client.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password,
        },
    )
    assert duplicate.status_code == 409

    login = client.post(
        "/api/v1/auth/login",
        data={"username": username, "password": password},
    )
    assert login.status_code == 200
    tokens = login.json()

    headers = {
        "Authorization": f"Bearer {tokens['access_token']}"
    }
    profile = client.get("/api/v1/users/me", headers=headers)
    assert profile.status_code == 200
    assert profile.json()["username"] == username

    refresh = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert refresh.status_code == 200
    replacement = refresh.json()

    # The original refresh token must not be reusable.
    reused = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert reused.status_code == 401

    logout = client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": replacement["refresh_token"]},
    )
    assert logout.status_code == 204

    after_logout = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": replacement["refresh_token"]},
    )
    assert after_logout.status_code == 401


def test_protected_profile_rejects_missing_token():
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401
