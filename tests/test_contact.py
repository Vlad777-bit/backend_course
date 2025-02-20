import pytest
from fastapi.testclient import TestClient
from app.main import app  # Импортируем приложение FastAPI, где подключены роутеры /contact

client = TestClient(app)

# ------------------------
# Тесты для /contact/basic
# ------------------------

def test_create_contact_valid():
    """
    Проверяем успешный запрос с корректными данными.
    Ожидаем статус 200 (OK) и наличие ключей "message" и "filename" в ответе.
    """
    payload = {
        "last_name": "Иванов",
        "first_name": "Иван",
        "date_of_birth": "1990-01-01",
        "phone": "+71234567890",
        "email": "ivanov@example.com"
    }
    response = client.post("/contact/basic", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Данные успешно сохранены"
    assert "filename" in data


def test_create_contact_invalid_names():
    """
    Проверяем валидацию ФИО (требуется заглавная буква и только кириллица).
    Ожидаем ошибку 422 (Unprocessable Entity).
    """
    payload = {
        "last_name": "ivanov",  # без заглавной
        "first_name": "Ivan",   # содержит латиницу
        "date_of_birth": "1990-01-01",
        "phone": "+71234567890",
        "email": "ivanov@example.com"
    }
    response = client.post("/contact/basic", json=payload)
    assert response.status_code == 422, response.text


def test_create_contact_invalid_phone():
    """
    Проверяем валидацию телефона.
    Ожидаем ошибку 422.
    """
    payload = {
        "last_name": "Иванов",
        "first_name": "Иван",
        "date_of_birth": "1990-01-01",
        "phone": "123",  # слишком короткий
        "email": "ivanov@example.com"
    }
    response = client.post("/contact/basic", json=payload)
    assert response.status_code == 422, response.text


def test_create_contact_invalid_email():
    """
    Проверяем валидацию email.
    Ожидаем ошибку 422.
    """
    payload = {
        "last_name": "Иванов",
        "first_name": "Иван",
        "date_of_birth": "1990-01-01",
        "phone": "+71234567890",
        "email": "ivanovexample.com"  # нет @
    }
    response = client.post("/contact/basic", json=payload)
    assert response.status_code == 422, response.text


# ---------------------------
# Тесты для /contact/extended
# ---------------------------

def test_create_extended_contact_valid():
    """
    Проверяем успешный запрос с корректными данными для расширенной модели.
    """
    payload = {
        "last_name": "Иванов",
        "first_name": "Иван",
        "date_of_birth": "1990-01-01",
        "phone": "+71234567890",
        "email": "ivanov@example.com",
        "reason": "нет доступа к сети",
        "detected_at": "2025-02-20T10:00:00"
    }
    response = client.post("/contact/extended", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Данные успешно сохранены"
    assert "filename" in data


def test_create_extended_contact_invalid_reason():
    """
    Проверяем валидацию поля 'reason'.
    Ожидаем ошибку 422, если причина не из списка допустимых.
    """
    payload = {
        "last_name": "Иванов",
        "first_name": "Иван",
        "date_of_birth": "1990-01-01",
        "phone": "+71234567890",
        "email": "ivanov@example.com",
        "reason": "другая причина",  # недопустимый вариант
        "detected_at": "2025-02-20T10:00:00"
    }
    response = client.post("/contact/extended", json=payload)
    assert response.status_code == 422, response.text


# ---------------------------------
# Тесты для /contact/multiple (3**)
# ---------------------------------

def test_create_contact_multiple_valid():
    """
    Проверяем успешный запрос с несколькими причинами.
    """
    payload = {
        "last_name": "Иванов",
        "first_name": "Иван",
        "date_of_birth": "1990-01-01",
        "phone": "+71234567890",
        "email": "ivanov@example.com",
        "reasons": ["нет доступа к сети", "не работает телефон"],
        "detected_at": "2025-02-20T10:00:00"
    }
    response = client.post("/contact/multiple", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Данные успешно сохранены"
    assert "filename" in data


def test_create_contact_multiple_invalid_reason():
    """
    Проверяем валидацию, когда хотя бы одна причина не соответствует списку.
    """
    payload = {
        "last_name": "Иванов",
        "first_name": "Иван",
        "date_of_birth": "1990-01-01",
        "phone": "+71234567890",
        "email": "ivanov@example.com",
        "reasons": ["нет доступа к сети", "другая причина"],
        "detected_at": "2025-02-20T10:00:00"
    }
    response = client.post("/contact/multiple", json=payload)
    assert response.status_code == 422, response.text
