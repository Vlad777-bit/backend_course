from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.repository.student_repository import StudentRepository
from app.utils.db import get_db

router = APIRouter()

@router.post("/import")
def import_students(csv_path: str = Query(..., description="Путь к файлу CSV"),
                    db: Session = Depends(get_db)):
    """
    Загрузка данных из CSV (students.csv) в таблицу 'students'.
    Пример вызова: POST /student/import?csv_path=students.csv
    """
    repo = StudentRepository(db)
    repo.insert_students_from_csv(csv_path)
    return {"message": "Данные успешно импортированы из CSV"}

@router.get("/by_faculty/{faculty_name}")
def get_students_by_faculty(faculty_name: str, db: Session = Depends(get_db)):
    """
    Возвращает список студентов по названию факультета.
    """
    repo = StudentRepository(db)
    return repo.get_students_by_faculty(faculty_name)

@router.get("/courses")
def get_unique_courses(db: Session = Depends(get_db)):
    """
    Возвращает список уникальных курсов.
    """
    repo = StudentRepository(db)
    return repo.get_unique_courses()

@router.get("/average/{faculty_name}")
def get_average_grade(faculty_name: str, db: Session = Depends(get_db)):
    """
    Возвращает средний балл по указанному факультету.
    """
    repo = StudentRepository(db)
    avg_grade = repo.get_average_grade_by_faculty(faculty_name)
    return {"faculty": faculty_name, "average_grade": avg_grade}

@router.get("/low_grade")
def get_students_by_course_low_grade(course: str,
                                     threshold: float = 30,
                                     db: Session = Depends(get_db)):
    """
    Возвращает список студентов по курсу 'course' с оценкой < 'threshold'.
    GET /student/low_grade?course=Математика-1&threshold=30
    """
    repo = StudentRepository(db)
    return repo.get_students_by_course_with_low_grade(course, threshold)
