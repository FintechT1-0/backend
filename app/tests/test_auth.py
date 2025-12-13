from fastapi.testclient import TestClient
from app.tests.api.auth import *
from app.tests.data.auth import * 


def test_register(client: TestClient):
    first = register_user(client, USER)
    assert first.status_code == 200

    second = register_user(client, SAME_EMAIL_USER)
    assert second.status_code == 400


def test_register_admin(client: TestClient):
    legitimate = register_admin(client, TRUE_ADMIN)
    assert legitimate.status_code == 200
    assert legitimate.json()["role"] == "admin"

    illegitimate = register_admin(client, FAKE_ADMIN)
    assert illegitimate.status_code == 403


def test_check_email(client: TestClient):
    first_check = check_email(client, EMAIL)
    assert first_check.status_code == 200
    assert first_check.json()["exists"] == False

    register_user(client, USER)

    second_check = check_email(client, EMAIL)
    assert second_check.status_code == 200
    assert second_check.json()["exists"] == True


def test_login(client: TestClient):
    register_user(client, USER)

    legitimate = login(client, USER_LOGIN)
    assert legitimate.status_code == 200

    illegitimate = login(client, USER_WRONG_PASS_LOGIN)
    assert illegitimate.status_code == 400


def test_me(client: TestClient):
    register_user(client, USER)
    
    user_data = login(client, USER_LOGIN)
    assert user_data.status_code == 200

    token = user_data.json()["token"]

    _me = me(client, token)
    assert _me.status_code == 200