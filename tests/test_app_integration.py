import pytest
import time
from fastapi.testclient import TestClient
from pathlib import Path

from app.main import app

client = TestClient(app)

@pytest.fixture(scope="function")  # <-- теперь "function" вместо "session"
def auth_token():
    """
    Регистрирует и логинит тестового пользователя.
    Возвращает access_token (Bearer).
    """
    # 1. Регистрация
    register_data = {
        "username": "testuser",
        "password": "testpass",
        "role": "user"
    }
    r = client.post("/auth/register", json=register_data)
    # Может вернуть 200 (успех) или 400 (если user уже есть)
    assert r.status_code in (200, 400)

    # 2. Логин
    login_data = {
        "username": "testuser",
        "password": "testpass"
    }
    r = client.post("/auth/login", json=login_data)
    assert r.status_code == 200, f"Login failed: {r.text}"
    token = r.json()["access_token"]
    return token

def test_login_wrong_password():
    """
    Проверяем, что при неверном пароле вернётся 401.
    """
    data = {
        "username": "testuser",  # Существующий логин (уже регистрировался в другом тесте)
        "password": "wrongpass"
    }
    r = client.post("/auth/login", json=data)
    assert r.status_code == 401, r.text

def test_logout(auth_token):
    """
    Проверяем логаут: после него токен становится недействительным.
    """
    headers = {"Authorization": f"Bearer {auth_token}"}
    r = client.post("/auth/logout", headers=headers)
    assert r.status_code == 200, r.text

    # Повторный запрос с тем же токеном должен дать 401
    r2 = client.get("/student/by_faculty?faculty=TestFaculty", headers=headers)
    assert r2.status_code == 401, r2.text

def test_import_csv_bg(auth_token, tmp_path):
    """
    Тестируем эндпойнт /student/import_csv_bg (фоновой импорт CSV).
    После вызова даём немного времени фоновой задаче, а потом проверяем,
    что импортированные данные действительно появились в БД.
    """
    # 1. Создаём временный CSV
    csv_data = """Фамилия,Имя,Факультет,Курс,Оценка
Иванов,Иван,Факультет Математики,Math-1,45
Сидоров,Сергей,Факультет Математики,Math-1,28
"""
    csv_file = tmp_path / "students.csv"
    csv_file.write_text(csv_data, encoding="utf-8")

    # 2. Запускаем импорт в фоне
    headers = {"Authorization": f"Bearer {auth_token}"}
    r = client.post(f"/student/import_csv_bg?csv_path={csv_file}", headers=headers)
    assert r.status_code == 200, r.text

    # 3. Ждём немного, чтобы фоновая задача успела выполниться
    time.sleep(0.5)

    # 4. Проверяем, что данные появились:
    #    Используем эндпойнт by_faculty (кэшируемый)
    r2 = client.get("/student/by_faculty?faculty=Факультет%20Математики", headers=headers)
    assert r2.status_code == 200, r2.text
    data = r2.json()
    names = [s["name"] for s in data]
    # Ожидаем "Иван Иванов" и "Сидоров Сергей"
    assert "Иван Иванов" in names
    assert "Сидоров Сергей" in names

def test_delete_bg(auth_token):
    """
    Тестируем эндпойнт /student/delete_bg (фоновое удаление).
    Создаём студента, потом удаляем его в фоне.
    """
    headers = {"Authorization": f"Bearer {auth_token}"}
    # 1. Создаём студента
    r = client.post("/student/create?name=ToDelete&faculty=TestFaculty&course=TestCourse&grade=99", headers=headers)
    assert r.status_code == 200, r.text
    created_id = r.json()["id"]

    # 2. Фоновое удаление
    r2 = client.delete(f"/student/delete_bg?ids={created_id}", headers=headers)
    assert r2.status_code == 200, r2.text

    time.sleep(0.5)  # даём время задаче отработать

    # 3. Проверяем, что студента нет
    r3 = client.get(f"/student/{created_id}", headers=headers)
    assert r3.status_code == 404, r3.text

def test_by_faculty_caching(auth_token):
    """
    Проверяем, что эндпойнт /student/by_faculty работает (200).
    Нельзя легко проверить "HIT"/"MISS" в автотестах, но убедимся,
    что запрос проходит и возвращает список.
    """
    headers = {"Authorization": f"Bearer {auth_token}"}
    r = client.get("/student/by_faculty?faculty=Факультет%20Математики", headers=headers)
    assert r.status_code == 200, r.text
    data = r.json()
    assert isinstance(data, list)

def test_crud_flow(auth_token):
    """
    Проверяем полный цикл CRUD:
      1) Create
      2) Read
      3) Update
      4) Read (проверяем изменения)
      5) Delete
      6) Read -> 404
    """
    headers = {"Authorization": f"Bearer {auth_token}"}

    # 1) Create
    r = client.post("/student/create?name=CRUDUser&faculty=TestFaculty&course=TestCourse&grade=100", headers=headers)
    assert r.status_code == 200, r.text
    created = r.json()
    st_id = created["id"]

    # 2) Read
    r2 = client.get(f"/student/{st_id}", headers=headers)
    assert r2.status_code == 200, r2.text
    st_data = r2.json()
    assert st_data["name"] == "CRUDUser"

    # 3) Update
    r3 = client.put(f"/student/{st_id}?name=UpdatedName&grade=75", headers=headers)
    assert r3.status_code == 200, r3.text
    updated = r3.json()
    assert updated["name"] == "UpdatedName"
    assert updated["grade"] == 75

    # 4) Read (проверяем изменения)
    r4 = client.get(f"/student/{st_id}", headers=headers)
    assert r4.status_code == 200, r4.text
    st_data2 = r4.json()
    assert st_data2["name"] == "UpdatedName"
    assert st_data2["grade"] == 75

    # 5) Delete
    r5 = client.delete(f"/student/{st_id}", headers=headers)
    assert r5.status_code == 200, r5.text

    # 6) Read -> 404
    r6 = client.get(f"/student/{st_id}", headers=headers)
    assert r6.status_code == 404, r6.text
