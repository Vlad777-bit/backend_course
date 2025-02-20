from fastapi.testclient import TestClient # type: ignore
from app.main import app

client = TestClient(app)

def test_add():
    response = client.get("/calculator/add?a=1&b=2")
    assert response.status_code == 200
    assert response.json() == {"result": 3}

def test_subtract():
    response = client.get("/calculator/subtract?a=5&b=3")
    assert response.status_code == 200
    assert response.json() == {"result": 2}

def test_multiply():
    response = client.get("/calculator/multiply?a=3&b=4")
    assert response.status_code == 200
    assert response.json() == {"result": 12}

def test_divide():
    response = client.get("/calculator/divide?a=10&b=2")
    assert response.status_code == 200
    assert response.json() == {"result": 5}
