from fastapi.testclient import TestClient
from app.tests.data.auth import USER, USER_LOGIN, TRUE_ADMIN, TRUE_ADMIN_LOGIN


def get_user(client: TestClient):
    register_user(client, USER)
    return login(client, USER_LOGIN).json()


def get_admin(client: TestClient):
    register_admin(client, TRUE_ADMIN)
    return login(client, TRUE_ADMIN_LOGIN).json()


def register_user(client: TestClient, user: dict):
    return client.post("/auth/register", json=user)


def register_admin(client: TestClient, admin: dict):
    return client.post("/auth/register/", json=admin)


def login(client: TestClient, user: dict):
    return client.post("/auth/login", json=user)


def check_email(client: TestClient, email: dict):
    return client.post("/auth/checkEmail", json=email)


def me(client: TestClient, token: str):
    return client.get("/auth/me", headers={
        "Authorization": f"Bearer {token}"
    })