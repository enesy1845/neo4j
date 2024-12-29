# tests/test_scenario.py

import pytest
from fastapi.testclient import TestClient
from main import app
from tools.database import init_db

client = TestClient(app)

@pytest.fixture(scope="session", autouse=True)
def setup_db():
    init_db()
    yield

def test_register_login():
    reg_payload = {
        "username": "teststudent",
        "password": "testpass",
        "name": "Test",
        "surname": "Student",
        "class_name": "7-a",
        "role": "student"
    }
    r = client.post("/auth/register", json=reg_payload)
    assert r.status_code == 200
    assert r.json()["message"] == "Registration successful."

    # login
    login_payload = {
        "username": "teststudent",
        "password": "testpass"
    }
    r = client.post("/auth/login", json=login_payload)
    assert r.status_code == 200
    token = r.json()["access_token"]
    assert token

    # Yetersiz rol => /users => 403 beklenir
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.get("/users/", headers=headers)
    assert resp.status_code == 403
