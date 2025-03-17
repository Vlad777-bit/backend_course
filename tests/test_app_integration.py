import pytest
from fastapi.testclient import TestClient
import time
from pathlib import Path

from app.main import app

client = TestClient(app)

@pytest.fixture(scope="function")
def auth_token():
    """
    Фикстура: регистрирует (если надо) и логинит тестового пользователя,
    возвращая Bearer-токен.
    """
    # 1) Попытка регистрации (допускаем 200 или 400, если уже есть)
    register_data = {
        "username": "testuser",
        "password": "testpass",
        "role": "user"
    }
    r = client.post("/auth/register", json=register_data)
    assert r.status_code in (200, 400)

    # 2) Логин
    login_data = {
        "username": "testuser",
        "password": "testpass"
    }
    r = client.post("/auth/login", json=login_data)
    assert r.status_code == 200, r.text

    token = r.json()["access_token"]
    return token

# --------------------------------------------------
# 1. Тесты для /auth/register (2 теста)
# --------------------------------------------------

def test_register_ok():
    """
    Успешная регистрация нового пользователя.
    """
    data = {
        "username": "unique_user",
        "password": "somepass",
        "role": "user"
    }
    r = client.post("/auth/register", json=data)
    # 200 = успех, 400 = такой user уже есть
    assert r.status_code in (200, 400), r.text

def test_register_conflict():
    """
    Повторная регистрация того же пользователя -> 400.
    """
    data = {
        "username": "testuser",
        "password": "anypass",
        "role": "user"
    }
    r = client.post("/auth/register", json=data)
    assert r.status_code == 400, r.text

# --------------------------------------------------
# 2. Тесты для /auth/login (2 теста)
# --------------------------------------------------

def test_login_ok():
    """
    Успешный логин.
    """
    data = {
        "username": "testuser",
        "password": "testpass"
    }
    r = client.post("/auth/login", json=data)
    assert r.status_code == 200, r.text
    resp = r.json()
    assert "access_token" in resp

def test_login_wrong_password():
    """
    Неверный пароль -> 401.
    """
    data = {
        "username": "testuser",
        "password": "wrongpass"
    }
    r = client.post("/auth/login", json=data)
    assert r.status_code == 401, r.text

# --------------------------------------------------
# 3. Тесты для /auth/logout (2 теста)
# --------------------------------------------------

def test_logout_ok(auth_token):
    """
    Успешный логаут. После него токен становится невалидным.
    """
    headers = {"Authorization": f"Bearer {auth_token}"}
    r = client.post("/auth/logout", headers=headers)
    assert r.status_code == 200, r.text

    # Теперь токен недействителен
    r2 = client.get("/student/unique_courses", headers=headers)
    # Ожидаем 401, если эндпойнт требует авторизации
    assert r2.status_code == 401, r2.text

def test_logout_no_token():
    """
    Без токена -> 401.
    """
    r = client.post("/auth/logout")
    assert r.status_code == 401, r.text

# --------------------------------------------------
# 4. Тесты для /student/import_csv (2 теста)
# --------------------------------------------------

def test_import_csv_ok(auth_token, tmp_path):
    """
    Успешный импорт CSV (POST /student/import_csv).
    """
    csv_data = """Фамилия,Имя,Факультет,Курс,Оценка
Иванов,Иван,Факультет Математики,Математика-1,45
Петров,Пётр,Факультет Математики,Математика-1,28
"""
    csv_file = tmp_path / "students.csv"
    csv_file.write_text(csv_data, encoding="utf-8")

    headers = {"Authorization": f"Bearer {auth_token}"}
    r = client.post(f"/student/import_csv_bg?csv_path={csv_file}", headers=headers)
    assert r.status_code == 200, r.text
    # Проверяем, что вернулся success
    resp = r.json()
    # Допустим, вы возвращаете {"message": "Импорт запущен в фоне"} или что-то похожее
    assert "message" in resp

def test_import_csv_unauthorized(tmp_path):
    """
    Без авторизации -> 401 (если эндпойнт защищён).
    """
    csv_data = "Фамилия,Имя,Факультет,Курс,Оценка\n..."
    csv_file = tmp_path / "students.csv"
    csv_file.write_text(csv_data, encoding="utf-8")

    r = client.post(f"/student/import_csv_bg?csv_path={csv_file}")
    assert r.status_code == 401, r.text

# --------------------------------------------------
# 5. Тесты для /student/unique_courses (2 теста)
# --------------------------------------------------

def test_unique_courses_ok(auth_token):
    """
    Успешный вызов /student/unique_courses.
    """
    headers = {"Authorization": f"Bearer {auth_token}"}
    r = client.get("/student/unique_courses", headers=headers)
    assert r.status_code == 200, r.text
    data = r.json()
    # Проверяем, что это список (или что-то ещё)
    assert isinstance(data, list)

def test_unique_courses_no_token():
    """
    Без токена -> 401.
    """
    r = client.get("/student/unique_courses")
    assert r.status_code == 401, r.text
