from fastapi.testclient import TestClient
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import app

client = TestClient(app)

def test_login_success():
    res = client.post("/users/login?username=admin&password=123")
    assert res.status_code == 200
    assert "token" in res.json()

def test_login_fail():
    res = client.post("/users/login?username=admin&password=wrong")
    assert res.status_code == 401

def test_me_without_token():
    res = client.get("/users/me")
    assert res.status_code == 401

def test_create_user():
    res = client.post("/users/", json={"username": "testuser", "email": "tests@tests.com"})
    assert res.status_code == 200
    assert res.json()["username"] == "testuser"