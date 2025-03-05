import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.student_models import Base, Student
from app.repository.student_repository import StudentRepository
import csv

@pytest.fixture
def in_memory_engine():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    return engine

@pytest.fixture
def db_session(in_memory_engine):
    Session = sessionmaker(bind=in_memory_engine)
    session = Session()
    yield session
    session.close()

@pytest.fixture
def student_repo(db_session):
    return StudentRepository(db_session)

def test_insert_students_from_csv(student_repo, db_session, tmp_path):
    """
    Проверяем метод insert_students_from_csv:
    - Создаём временный CSV с русскими заголовками
    - Импортируем
    - Проверяем, что данные появились
    """
    csv_data = """Фамилия,Имя,Факультет,Курс,Оценка
Иванов,Иван,Факультет Математики,Математика-1,45
Петров,Пётр,Факультет Математики,Математика-1,28
Сидорова,Мария,Факультет Физики,Физика-2,55
"""
    csv_file = tmp_path / "students.csv"
    csv_file.write_text(csv_data, encoding="utf-8")

    student_repo.insert_students_from_csv(str(csv_file))

    all_students = db_session.query(Student).all()
    assert len(all_students) == 3

def test_get_students_by_faculty(student_repo, db_session):
    """
    Тестируем метод get_students_by_faculty.
    Добавляем вручную студентов с единым полем name.
    """
    s1 = Student(name="Иван Иванов",
                 faculty="Факультет Математики",
                 course="Математика-1",
                 grade=45)
    s2 = Student(name="Пётр Петров",
                 faculty="Факультет Математики",
                 course="Математика-1",
                 grade=28)
    s3 = Student(name="Мария Сидорова",
                 faculty="Факультет Физики",
                 course="Физика-2",
                 grade=55)
    db_session.add_all([s1, s2, s3])
    db_session.commit()

    students_math = student_repo.get_students_by_faculty("Факультет Математики")
    assert len(students_math) == 2
    for student in students_math:
        assert student.faculty == "Факультет Математики"

def test_get_unique_courses(student_repo, db_session):
    """
    Тестируем метод get_unique_courses.
    """
    s1 = Student(name="Иван Иванов",
                 faculty="Факультет Математики",
                 course="Математика-1",
                 grade=45)
    s2 = Student(name="Пётр Петров",
                 faculty="Факультет Математики",
                 course="Математика-1",
                 grade=28)
    s3 = Student(name="Мария Сидорова",
                 faculty="Факультет Физики",
                 course="Физика-2",
                 grade=55)
    db_session.add_all([s1, s2, s3])
    db_session.commit()

    courses = student_repo.get_unique_courses()
    assert len(courses) == 2
    assert "Математика-1" in courses
    assert "Физика-2" in courses

def test_get_average_grade_by_faculty(student_repo, db_session):
    """
    Тестируем метод get_average_grade_by_faculty.
    """
    s1 = Student(name="Иван Иванов",
                 faculty="Факультет Математики",
                 course="Математика-1",
                 grade=45)
    s2 = Student(name="Пётр Петров",
                 faculty="Факультет Математики",
                 course="Математика-1",
                 grade=30)
    s3 = Student(name="Мария Сидорова",
                 faculty="Факультет Физики",
                 course="Физика-2",
                 grade=55)
    db_session.add_all([s1, s2, s3])
    db_session.commit()

    avg_math = student_repo.get_average_grade_by_faculty("Факультет Математики")
    # (45 + 30) / 2 = 37.5
    assert pytest.approx(avg_math, 0.01) == 37.5

    avg_phys = student_repo.get_average_grade_by_faculty("Факультет Физики")
    assert pytest.approx(avg_phys, 0.01) == 55

def test_get_students_by_course_with_low_grade(student_repo, db_session):
    """
    Тестируем метод get_students_by_course_with_low_grade.
    """
    s1 = Student(name="Иван Иванов",
                 faculty="Факультет Математики",
                 course="Математика-1",
                 grade=45)
    s2 = Student(name="Пётр Петров",
                 faculty="Факультет Математики",
                 course="Математика-1",
                 grade=28)
    s3 = Student(name="Мария Сидорова",
                 faculty="Факультет Физики",
                 course="Физика-2",
                 grade=55)
    db_session.add_all([s1, s2, s3])
    db_session.commit()

    low_grade_students = student_repo.get_students_by_course_with_low_grade("Математика-1", threshold=30)
    assert len(low_grade_students) == 1
    assert low_grade_students[0].name == "Пётр Петров"
    assert low_grade_students[0].grade == 28
