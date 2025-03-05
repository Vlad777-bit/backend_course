from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.repository.student_repository import StudentRepository
from app.schemas.student_schemas import (
    StudentCreate,
    StudentUpdate,
    StudentOut
)
from app.utils.db import get_db  # функция, возвращающая объект Session

router = APIRouter()

@router.post("/import_csv")
def import_students(csv_path: str = Query(..., description="Путь к CSV-файлу"),
                    db: Session = Depends(get_db)):
    """
    Пример: импорт из CSV (Фамилия,Имя,Факультет,Курс,Оценка)
    """
    repo = StudentRepository(db)
    repo.insert_students_from_csv(csv_path)
    return {"message": "CSV imported successfully"}

@router.get("/by_faculty")
def get_students_by_faculty(faculty: str, db: Session = Depends(get_db)):
    """
    Получение списка студентов по названию факультета
    """
    repo = StudentRepository(db)
    return repo.get_students_by_faculty(faculty)

@router.get("/unique_courses")
def get_unique_courses(db: Session = Depends(get_db)):
    """
    Список уникальных курсов
    """
    repo = StudentRepository(db)
    return repo.get_unique_courses()

@router.get("/average_grade")
def get_average_grade(faculty: str, db: Session = Depends(get_db)):
    """
    Средняя оценка по факультету
    """
    repo = StudentRepository(db)
    avg_value = repo.get_average_grade_by_faculty(faculty)
    return {"faculty": faculty, "average_grade": avg_value}

@router.get("/low_grade")
def get_students_by_course_with_low_grade(course: str, threshold: float = 30, db: Session = Depends(get_db)):
    """
    Список студентов по курсу, у которых оценка < threshold
    """
    repo = StudentRepository(db)
    return repo.get_students_by_course_with_low_grade(course, threshold)

# ---------------------------
# CRUD-эндпойнты
# ---------------------------

@router.post("/create", response_model=StudentOut)
def create_student(student_data: StudentCreate, db: Session = Depends(get_db)):
    repo = StudentRepository(db)
    new_student = repo.create_student(
        name=student_data.name,
        faculty=student_data.faculty,
        course=student_data.course,
        grade=student_data.grade
    )
    return new_student

@router.get("/{student_id}", response_model=StudentOut)
def get_student(student_id: int, db: Session = Depends(get_db)):
    repo = StudentRepository(db)
    student = repo.get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@router.put("/{student_id}", response_model=StudentOut)
def update_student(student_id: int, update_data: StudentUpdate, db: Session = Depends(get_db)):
    repo = StudentRepository(db)
    updated = repo.update_student(
        student_id=student_id,
        name=update_data.name,
        faculty=update_data.faculty,
        course=update_data.course,
        grade=update_data.grade
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Student not found")
    return updated

@router.delete("/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    repo = StudentRepository(db)
    success = repo.delete_student(student_id)
    if not success:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"message": f"Student with id={student_id} deleted successfully."}
