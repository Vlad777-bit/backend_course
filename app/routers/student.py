from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.repository.student_repository import StudentRepository
from app.utils.db import get_db
from app.utils.dependencies import get_current_user

router = APIRouter()

@router.post("/import_csv")
def import_students(
    csv_path: str = Query(..., description="Путь к CSV-файлу"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Импорт из CSV-файла (Фамилия,Имя,Факультет,Курс,Оценка).
    Только для авторизованных пользователей.
    """
    repo = StudentRepository(db)
    repo.insert_students_from_csv(csv_path)
    return {"message": "CSV imported successfully"}

@router.get("/by_faculty")
def get_students_by_faculty(
    faculty: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Получение списка студентов по названию факультета.
    Только для авторизованных пользователей.
    """
    repo = StudentRepository(db)
    return repo.get_students_by_faculty(faculty)

@router.get("/unique_courses")
def get_unique_courses(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Список уникальных курсов.
    Только для авторизованных пользователей.
    """
    repo = StudentRepository(db)
    return repo.get_unique_courses()

@router.get("/average_grade")
def get_average_grade(
    faculty: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Средняя оценка по факультету.
    Только для авторизованных пользователей.
    """
    repo = StudentRepository(db)
    avg_value = repo.get_average_grade_by_faculty(faculty)
    return {"faculty": faculty, "average_grade": avg_value}

@router.get("/low_grade")
def get_students_by_course_with_low_grade(
    course: str,
    threshold: float = 30,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Список студентов по курсу, у которых оценка < threshold (по умолчанию 30).
    Только для авторизованных пользователей.
    """
    repo = StudentRepository(db)
    return repo.get_students_by_course_with_low_grade(course, threshold)

# ---------------------------
# Ниже CRUD-эндпойнты
# ---------------------------

@router.post("/create")
def create_student(
    name: str,
    faculty: str,
    course: str,
    grade: float,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Создать новую запись (Create).
    Только для авторизованных пользователей.
    """
    repo = StudentRepository(db)
    new_stud = repo.create_student(name, faculty, course, grade)
    return {"id": new_stud.id, "message": "Student created"}

@router.get("/{student_id}")
def read_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Получить информацию об одном студенте (Read).
    Только для авторизованных пользователей.
    """
    repo = StudentRepository(db)
    student = repo.get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return {
        "id": student.id,
        "name": student.name,
        "faculty": student.faculty,
        "course": student.course,
        "grade": student.grade
    }

@router.put("/{student_id}")
def update_student(
    student_id: int,
    name: str = None,
    faculty: str = None,
    course: str = None,
    grade: float = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Обновить данные студента (Update).
    Только для авторизованных пользователей.
    """
    repo = StudentRepository(db)
    updated = repo.update_student(student_id, name, faculty, course, grade)
    if not updated:
        raise HTTPException(status_code=404, detail="Student not found")
    return {
        "id": updated.id,
        "name": updated.name,
        "faculty": updated.faculty,
        "course": updated.course,
        "grade": updated.grade
    }

@router.delete("/{student_id}")
def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Удалить студента (Delete).
    Только для авторизованных пользователей.
    """
    repo = StudentRepository(db)
    success = repo.delete_student(student_id)
    if not success:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"message": f"Student with id={student_id} deleted successfully."}
