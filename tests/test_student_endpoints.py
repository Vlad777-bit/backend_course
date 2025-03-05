import pytest
from fastapi.testclient import TestClient
from pathlib import Path

from app.main import app

client = TestClient(app)

# ---------------------------------------------------------
# 1. Вспомогательная фикстура для регистрации + логина
# ---------------------------------------------------------
@pytest.fixture
def auth_token():
    """
    Регистрирует и логинит тестового пользователя.
    Возвращает access_token (Bearer).
    """
    # 1. Регистрируем
    register_data = {
        "username": "testuser",
        "password": "testpass",
        "role": "user"
    }
    r = client.post("/auth/register", json=register_data)
    assert r.status_code in (200, 400), r.text
    # Если пользователь уже существует, вернётся 400, тогда продолжаем

    # 2. Логиним
    login_data = {
        "username": "testuser",
        "password": "testpass"
    }
    r = client.post("/auth/login", json=login_data)
    assert r.status_code == 200, r.text

    token = r.json()["access_token"]
    return token


# ---------------------------------------------------------
# 2. Тестируем эндпойнты /auth
# ---------------------------------------------------------

def test_register_new_user():
    """
    Проверяем успешную регистрацию нового пользователя.
    """
    data = {
        "username": "unique_user",
        "password": "pass123",
        "role": "read_only"
    }
    r = client.post("/auth/register", json=data)
    # Могут быть 200 (успешно) или 400 (если такой user уже есть)
    assert r.status_code in (200, 400)

def test_login_wrong_password():
    """
    Проверяем, что при неверном пароле вернётся 401.
    """
    data = {
        "username": "testuser",   # фиктивный или существующий
        "password": "wrongpass"
    }
    r = client.post("/auth/login", json=data)
    assert r.status_code == 401, r.text

def test_logout(auth_token):
    """
    Проверяем, что logout работает (200).
    """
    headers = {"Authorization": f"Bearer {auth_token}"}
    r = client.post("/auth/logout", headers=headers)
    assert r.status_code == 200, r.text

    # После логаута тот же токен не должен работать
    r2 = client.get("/student/unique_courses", headers=headers)
    assert r2.status_code == 401, r2.text


# ---------------------------------------------------------
# 3. Тестируем эндпойнты /student
# ---------------------------------------------------------

def test_unauthorized_access():
    """
    Проверяем, что без токена эндпойнты /student недоступны (401).
    """
    r = client.get("/student/unique_courses")
    assert r.status_code == 401, r.text

def test_import_csv(auth_token, tmp_path):
    """
    Тестируем эндпойнт /student/import_csv (POST).
    Передаём путь к временному CSV, проверяем 200 и корректную обработку.
    """
    csv_data = """Фамилия,Имя,Факультет,Курс,Оценка
Иванов,Иван,Факультет Математики,Математика-1,45
Петров,Пётр,Факультет Математики,Математика-1,28
Сидорова,Мария,Факультет Физики,Физика-2,55
"""
    csv_file = tmp_path / "students.csv"
    csv_file.write_text(csv_data, encoding="utf-8")

    headers = {"Authorization": f"Bearer {auth_token}"}
    r = client.post("/student/import_csv?csv_path=" + str(csv_file), headers=headers)
    assert r.status_code == 200, r.text
    assert r.json()["message"] == "CSV imported successfully"

def test_create_student(auth_token):
    """
    Тестируем создание студента (POST /student/create).
    """
    headers = {"Authorization": f"Bearer {auth_token}"}
    payload = {
        "name": "Иван Иванов",
        "faculty": "Факультет Математики",
        "course": "Математика-2",
        "grade": 50
    }
    r = client.post("/student/create", params=payload, headers=headers)
    assert r.status_code == 200, r.text
    data = r.json()
    assert "id" in data
    assert data["message"] == "Student created"

def test_get_unique_courses(auth_token):
    """
    Проверяем GET /student/unique_courses (после импорта CSV или create).
    """
    headers = {"Authorization": f"Bearer {auth_token}"}
    r = client.get("/student/unique_courses", headers=headers)
    assert r.status_code == 200, r.text
    # Может вернуться ["Математика-1", "Физика-2", "Математика-2"], в зависимости от тестов
    courses = r.json()
    assert isinstance(courses, list)

def test_average_grade(auth_token):
    """
    Тестируем GET /student/average_grade
    """
    headers = {"Authorization": f"Bearer {auth_token}"}
    # Предположим, что "Факультет Математики" уже есть в БД
    r = client.get("/student/average_grade?faculty=Факультет%20Математики", headers=headers)
    assert r.status_code == 200, r.text
    data = r.json()
    assert "average_grade" in data

def test_crud_operations(auth_token):
    """
    Полный цикл CRUD: create -> read -> update -> read -> delete -> read(404).
    """
    headers = {"Authorization": f"Bearer {auth_token}"}

    # 1) Create
    r = client.post("/student/create?name=Test%20Student&faculty=TestFaculty&course=TestCourse&grade=100", headers=headers)
    assert r.status_code == 200, r.text
    created = r.json()
    student_id = created["id"]

    # 2) Read
    r2 = client.get(f"/student/{student_id}", headers=headers)
    assert r2.status_code == 200, r2.text
    st_data = r2.json()
    assert st_data["name"] == "Test Student"

    # 3) Update
    r3 = client.put(
        f"/student/{student_id}?name=Updated%20Name&grade=75",
        headers=headers
    )
    assert r3.status_code == 200, r3.text
    updated = r3.json()
    assert updated["name"] == "Updated Name"
    assert updated["grade"] == 75

    # 4) Read (проверяем изменения)
    r4 = client.get(f"/student/{student_id}", headers=headers)
    assert r4.status_code == 200, r4.text
    st_data2 = r4.json()
    assert st_data2["name"] == "Updated Name"
    assert st_data2["grade"] == 75

    # 5) Delete
    r5 = client.delete(f"/student/{student_id}", headers=headers)
    assert r5.status_code == 200, r5.text
    assert "deleted successfully" in r5.json()["message"]

    # 6) Read (должен вернуть 404)
    r6 = client.get(f"/student/{student_id}", headers=headers)
    assert r6.status_code == 404, r6.text
