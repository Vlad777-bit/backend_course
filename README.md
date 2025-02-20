# Домашнее задание: **2 к теме 2 (дедлайн 19.02.25)** 🚀

![FastAPI Logo](https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png)

---

## 📚 Общая информация

-   **Дисциплина:** Разработка прототипов программных решений
-   **Тема:** FastAPI и Pydantic
-   **Преподаватель:** Владимир Хомутов
-   **Время выполнения:** 2 часа
-   **Дедлайн:** 7 дней после окончания вебинара

---

## 🎯 Цель задания

Научиться создавать простой сервис на основе FastAPI и Pydantic.

---

## 📝 Описание задания

### Задание 1

Создайте сервис для сбора обращений абонентов на основе FastAPI. Эндпойнт должен принимать следующие атрибуты:

-   **Фамилия:** должна начинаться с заглавной буквы и содержать только кириллицу.
-   **Имя:** должно начинаться с заглавной буквы и содержать только кириллицу.
-   **Дата рождения**
-   **Номер телефона**
-   **E-mail**

Все переданные атрибуты должны валидироваться с помощью модели **Pydantic**. Результат сохраняется на диске в виде JSON-файла, содержащего переданные данные.

### Задание 2\* (необязательное, повышенная сложность)

Добавьте в сервис следующие атрибуты:

-   **Причина обращения:** возможные значения – "нет доступа к сети", "не работает телефон", "не приходят письма".
-   **Дата и время обнаружения проблемы.**

Все новые атрибуты также должны валидироваться с помощью модели **Pydantic**.

### Задание 3\*\* (необязательное, высокая сложность)

Расширьте функционал сервиса так, чтобы в одном запросе можно было передавать несколько причин обращения. При этом все атрибуты должны проходить валидацию с помощью модели **Pydantic**.

---

## 🛠 Инструменты

-   **IDE:** Visual Studio Code, PyCharm
-   **Язык программирования:** Python
-   **Фреймворк:** [FastAPI](https://fastapi.tiangolo.com/)
-   **Модель валидации:** [Pydantic](https://pydantic-docs.helpmanual.io/)

---

## ✅ Чек-лист самопроверки

Перед сдачей работы убедитесь, что выполнены следующие пункты:

| **Критерии выполнения задания**                                                                     | **Статус** |
| --------------------------------------------------------------------------------------------------- | :--------: |
| Разработана Pydantic-модель для предложенной модели данных                                          |     ✅     |
| Разработан эндпойнт для получения данных от пользователя                                            |     ✅     |
| Разработан валидатор для фамилии и имени (проверка заглавной буквы, отсутствие спецсимволов и цифр) |     ✅     |
| Разработаны валидаторы для номера телефона, e-mail и даты                                           |     ✅     |

**Задание считается выполненным, если:**

-   Прикреплена ссылка на файл с выполненным заданием.
-   Доступ к файлу открыт.
-   Код корректно решает поставленную задачу.

**Задание не выполнено, если:**

-   Файл с заданием не прикреплён или отсутствует доступ по ссылке.
-   Код выдаёт ошибку или возвращает неправильный результат.

---

## 🚀 Запуск проекта

Чтобы запустить проект на локальной машине, выполните следующие шаги:

1. **Клонируйте репозиторий:**

    ```bash
    git clone git@github.com:Vlad777-bit/backend_course.git
    ```

2. **Перейдите в директорию проекта:**

    ```bash
    cd backend_course
    ```

3. **Переключиться на ветку:**

    ```bash
    git checkout hw_02
    ```

4. **Установите зависимости:**

    ```bash
    pip install -r requirements.txt
    ```

5. **Запустите проект:**

    ```bash
    python -m app.main
    ```

6. **Запустите тесты:**

    ```bash
    pytest
    ```

7. **Проверьте работу приложения:**

    Откройте в браузере http://127.0.0.1:8000 или перейдите по адресу документации http://127.0.0.1:8000/docs. Документы хранятся по пути ./app/storage

## 👤 Автор

Ножкин Владислав

[GitHub](https://github.com/Vlad777-bit) профиль

## 📄 Лицензия

Этот проект лицензирован под лицензией MIT.

## 🔗 Ссылки

Ссылка на задание в [Нетологии](https://netology.ru/profile/program/bhebdps-rppr-23-4/lessons/465175/lesson_items/2536190)
