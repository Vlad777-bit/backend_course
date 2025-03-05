import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.student_models import Base, Student
from app.repository.student_repository import StudentRepository

@pytest.fixture
def in_memory_engine():
    """
    Создаёт движок SQLite в памяти и генерирует таблицы.
    """
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    return engine

@pytest.fixture
def db_session(in_memory_engine):
    """
    Создаёт и отдаёт сессию, а после теста закрывает её.
    """
    Session = sessionmaker(bind=in_memory_engine)
    session = Session()
    yield session
    session.close()

@pytest.fixture
def student_repo(db_session):
    """
    Возвращает объект репозитория, связанный с in-memory сессией.
    """
    return StudentRepository(db_session)


# ------------------------------------------------------
# 1. Тест insert_students_from_csv
# ------------------------------------------------------
def test_insert_students_from_csv(student_repo, db_session, tmp_path):
    """
    Проверяем импорт CSV (Фамилия,Имя,Факультет,Курс,Оценка).
    Убеждаемся, что записи корректно создаются.
    """
    csv_data = """Фамилия,Имя,Факультет,Курс,Оценка
Иванов,Иван,Факультет Математики,Математика-1,45
Петров,Пётр,Факультет Математики,Математика-1,28
Сидорова,Мария,Факультет Физики,Физика-2,55
"""
    # Создаём временный CSV-файл
    csv_file = tmp_path / "students.csv"
    csv_file.write_text(csv_data, encoding="utf-8")

    # Вызываем метод для импорта
    student_repo.insert_students_from_csv(str(csv_file))

    # Проверяем, что в БД есть 3 записи
    all_students = db_session.query(Student).all()
    assert len(all_students) == 3

    # Проверяем, что данные корректно считаны
    names = [s.name for s in all_students]
    assert "Иванов Иван" in names
    assert "Петров Пётр" in names
    assert "Сидорова Мария" in names


# ------------------------------------------------------
# 2. Тест get_students_by_faculty
# ------------------------------------------------------
def test_get_students_by_faculty(student_repo, db_session):
    """
    Проверяем выборку по названию факультета.
    """
    s1 = Student(name="Иван Иванов", faculty="Факультет Математики", course="Математика-1", grade=45)
    s2 = Student(name="Пётр Петров", faculty="Факультет Математики", course="Математика-1", grade=28)
    s3 = Student(name="Мария Сидорова", faculty="Факультет Физики", course="Физика-2", grade=55)
    db_session.add_all([s1, s2, s3])
    db_session.commit()

    # Запрашиваем студентов факультета "Факультет Математики"
    result = student_repo.get_students_by_faculty("Факультет Математики")
    assert len(result) == 2
    assert all(st.faculty == "Факультет Математики" for st in result)


# ------------------------------------------------------
# 3. Тест get_unique_courses
# ------------------------------------------------------
def test_get_unique_courses(student_repo, db_session):
    """
    Проверяем получение списка уникальных курсов.
    """
    s1 = Student(name="Иван Иванов", faculty="Факультет Математики", course="Математика-1", grade=45)
    s2 = Student(name="Пётр Петров", faculty="Факультет Математики", course="Математика-1", grade=28)
    s3 = Student(name="Мария Сидорова", faculty="Факультет Физики", course="Физика-2", grade=55)
    db_session.add_all([s1, s2, s3])
    db_session.commit()

    courses = student_repo.get_unique_courses()
    # Должны получить два уникальных курса
    assert len(courses) == 2
    assert "Математика-1" in courses
    assert "Физика-2" in courses


# ------------------------------------------------------
# 4. Тест get_average_grade_by_faculty
# ------------------------------------------------------
def test_get_average_grade_by_faculty(student_repo, db_session):
    """
    Проверяем получение среднего балла по факультету.
    """
    s1 = Student(name="Иван Иванов", faculty="Факультет Математики", course="Математика-1", grade=45)
    s2 = Student(name="Пётр Петров", faculty="Факультет Математики", course="Математика-1", grade=30)
    s3 = Student(name="Мария Сидорова", faculty="Факультет Физики", course="Физика-2", grade=55)
    db_session.add_all([s1, s2, s3])
    db_session.commit()

    avg_math = student_repo.get_average_grade_by_faculty("Факультет Математики")
    assert avg_math is not None
    assert abs(avg_math - 37.5) < 1e-6  # (45 + 30) / 2 = 37.5

    avg_phys = student_repo.get_average_grade_by_faculty("Факультет Физики")
    assert abs(avg_phys - 55) < 1e-6

    avg_unknown = student_repo.get_average_grade_by_faculty("Неизвестный факультет")
    assert avg_unknown is None


# ------------------------------------------------------
# 5. Тест get_students_by_course_with_low_grade
# ------------------------------------------------------
def test_get_students_by_course_with_low_grade(student_repo, db_session):
    """
    Проверяем выбор студентов по курсу с оценкой ниже порога.
    """
    s1 = Student(name="Иван Иванов", faculty="Факультет Математики", course="Математика-1", grade=45)
    s2 = Student(name="Пётр Петров", faculty="Факультет Математики", course="Математика-1", grade=28)
    s3 = Student(name="Мария Сидорова", faculty="Факультет Физики", course="Физика-2", grade=55)
    db_session.add_all([s1, s2, s3])
    db_session.commit()

    result = student_repo.get_students_by_course_with_low_grade("Математика-1", threshold=30)
    assert len(result) == 1
    assert result[0].name == "Пётр Петров"
    assert result[0].grade == 28


# ------------------------------------------------------
# 6. Тест create_student (CRUD - Create)
# ------------------------------------------------------
def test_create_student(student_repo, db_session):
    """
    Проверяем создание новой записи.
    """
    new_stud = student_repo.create_student(
        name="Новый Студент",
        faculty="Факультет Тестов",
        course="Тест-101",
        grade=99.5
    )
    assert new_stud.id is not None
    assert new_stud.name == "Новый Студент"

    # Убедимся, что запись реально появилась в БД
    db_stud = db_session.query(Student).filter_by(id=new_stud.id).first()
    assert db_stud is not None
    assert db_stud.name == "Новый Студент"


# ------------------------------------------------------
# 7. Тест get_student_by_id (CRUD - Read)
# ------------------------------------------------------
def test_get_student_by_id(student_repo, db_session):
    """
    Проверяем чтение одной записи по ID.
    """
    s1 = Student(name="Студент1", faculty="Факультет1", course="Курс1", grade=10)
    s2 = Student(name="Студент2", faculty="Факультет2", course="Курс2", grade=20)
    db_session.add_all([s1, s2])
    db_session.commit()

    # Ищем s1
    found = student_repo.get_student_by_id(s1.id)
    assert found is not None
    assert found.name == "Студент1"

    # Если ID не существует, должно вернуться None
    missing = student_repo.get_student_by_id(9999)
    assert missing is None


# ------------------------------------------------------
# 8. Тест update_student (CRUD - Update)
# ------------------------------------------------------
def test_update_student(student_repo, db_session):
    """
    Проверяем обновление существующей записи.
    """
    s1 = Student(name="Студент1", faculty="Факультет1", course="Курс1", grade=10)
    db_session.add(s1)
    db_session.commit()

    updated = student_repo.update_student(
        student_id=s1.id,
        name="Обновлённый Студент",
        grade=45.0
    )
    assert updated is not None
    assert updated.name == "Обновлённый Студент"
    assert updated.grade == 45.0

    # Проверяем в БД
    db_stud = db_session.get(Student, s1.id)
    assert db_stud.name == "Обновлённый Студент"
    assert db_stud.grade == 45.0

    # Если студент не найден
    no_student = student_repo.update_student(
        student_id=9999,
        name="Никто"
    )
    assert no_student is None


# ------------------------------------------------------
# 9. Тест delete_student (CRUD - Delete)
# ------------------------------------------------------
def test_delete_student(student_repo, db_session):
    """
    Проверяем удаление записи.
    """
    s1 = Student(name="Студент1", faculty="Факультет1", course="Курс1", grade=10)
    db_session.add(s1)
    db_session.commit()

    # Удаляем
    success = student_repo.delete_student(s1.id)
    assert success is True

    # Запись должна исчезнуть
    found = db_session.query(Student).filter_by(id=s1.id).first()
    assert found is None

    # Повторное удаление должно вернуть False
    again = student_repo.delete_student(s1.id)
    assert again is False
