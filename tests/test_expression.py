from fastapi.testclient import TestClient # type: ignore
from app.main import app

client = TestClient(app)

def test_set_full_expression():
    data = {"expr": "(1+2)*3"}
    response = client.post("/expression/full", json=data)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data.get("result") == 9

def test_evaluate_without_expression():
    # Если глобальное выражение не установлено, должно возвращаться сообщение об ошибке
    response = client.post("/expression/evaluate")
    if response.status_code == 400:
        assert "Выражение не задано" in response.json()["detail"]
