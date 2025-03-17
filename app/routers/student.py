from fastapi import APIRouter, BackgroundTasks, Query, Depends, HTTPException
from typing import List
import json

from sqlalchemy.orm import Session
from app.utils.db import get_db
from app.utils.redis_client import r
from app.repository.student_repository import StudentRepository
from app.tasks.student_tasks import import_csv_task, delete_students_task
from app.utils.dependencies import get_current_user

router = APIRouter()

# ---------------------------------------------------
# 1. Фоновые задачи (не кэшируем)
# ---------------------------------------------------

@router.post("/import_csv_bg")
def import_csv_in_background(
    csv_path: str = Query(..., description="Путь к CSV-файлу"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user=Depends(get_current_user),
):
    """
    Запускает импорт CSV в фоне.
    Пример: POST /student/import_csv_bg?csv_path=./students.csv
    """
    background_tasks.add_task(import_csv_task, csv_path)
    return {"message": f"Импорт для файла '{csv_path}' запущен в фоне."}


@router.delete("/delete_bg")
def delete_students_in_background(
    ids: List[int] = Query(..., description="Список ID для удаления"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user=Depends(get_current_user),
):
    """
    Удаляет записи (студентов) с переданными ID в фоне.
    Пример: DELETE /student/delete_bg?ids=1&ids=2
    """
    background_tasks.add_task(delete_students_task, ids)
    return {"message": f"Задача по удалению студентов с id {ids} запущена в фоне."}


# ---------------------------------------------------
# 2. КЭШИРУЕМЫЕ GET-эндпойнты
# ---------------------------------------------------

@router.get("/by_faculty")
def get_students_by_faculty(
    faculty: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Возвращает список студентов по факультету.
    Результат кэшируется в Redis на 60 секунд.
    """
    cache_key = f"by_faculty:{faculty}"
    cached = r.get(cache_key)
    if cached:
        print("[REDIS] HIT (by_faculty)")
        return json.loads(cached)

    print("[REDIS] MISS (by_faculty)")
    repo = StudentRepository(db)
    students = repo.get_students_by_faculty(faculty)
    result = [
        {
            "id": s.id,
            "name": s.name,
            "faculty": s.faculty,
            "course": s.course,
            "grade": s.grade
        }
        for s in students
    ]
    r.setex(cache_key, 60, json.dumps(result, ensure_ascii=False))
    return result


@router.get("/unique_courses")
def get_unique_courses(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Список уникальных курсов.
    Результат кэшируется на 60 секунд.
    """
    cache_key = "unique_courses"
    cached = r.get(cache_key)
    if cached:
        print("[REDIS] HIT (unique_courses)")
        return json.loads(cached)

    print("[REDIS] MISS (unique_courses)")
    repo = StudentRepository(db)
    courses = repo.get_unique_courses()
    # courses - это список строк
    r.setex(cache_key, 60, json.dumps(courses, ensure_ascii=False))
    return courses


@router.get("/average_grade")
def get_average_grade(
    faculty: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Средняя оценка по факультету.
    Кэшируем результат на 60 секунд.
    """
    cache_key = f"average_grade:{faculty}"
    cached = r.get(cache_key)
    if cached:
        print("[REDIS] HIT (average_grade)")
        return json.loads(cached)

    print("[REDIS] MISS (average_grade)")
    repo = StudentRepository(db)
    avg_val = repo.get_average_grade_by_faculty(faculty)
    # avg_val может быть float или None
    result = {"faculty": faculty, "average_grade": avg_val}
    r.setex(cache_key, 60, json.dumps(result, ensure_ascii=False))
    return result


@router.get("/low_grade")
def get_students_low_grade(
    course: str,
    threshold: float = 30,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Список студентов по курсу, у которых оценка < threshold (по умолчанию 30).
    Кэшируем результат на 60 секунд.
    """
    cache_key = f"low_grade:{course}:{threshold}"
    cached = r.get(cache_key)
    if cached:
        print("[REDIS] HIT (low_grade)")
        return json.loads(cached)

    print("[REDIS] MISS (low_grade)")
    repo = StudentRepository(db)
    students = repo.get_students_by_course_with_low_grade(course, threshold)
    result = [
        {
            "id": s.id,
            "name": s.name,
            "faculty": s.faculty,
            "course": s.course,
            "grade": s.grade
        }
        for s in students
    ]
    r.setex(cache_key, 60, json.dumps(result, ensure_ascii=False))
    return result


# ---------------------------------------------------
# 3. CRUD (Create/Read/Update/Delete)
# ---------------------------------------------------
# Обычно POST/PUT/DELETE не кэшируют. Но Read (GET) можно кэшировать.

@router.post("/create")
def create_student(
    name: str,
    faculty: str,
    course: str,
    grade: float,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Создать новую запись (не кэшируем).
    """
    repo = StudentRepository(db)
    new_st = repo.create_student(name, faculty, course, grade)
    return {"id": new_st.id, "message": "Student created"}

@router.get("/{student_id}")
def read_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Прочитать одного студента по ID.
    Кэшируем результат на 60 секунд.
    """
    cache_key = f"student_id:{student_id}"
    cached = r.get(cache_key)
    if cached:
        print("[REDIS] HIT (read_student)")
        return json.loads(cached)

    print("[REDIS] MISS (read_student)")
    repo = StudentRepository(db)
    st = repo.get_student_by_id(student_id)
    if not st:
        raise HTTPException(status_code=404, detail="Student not found")

    result = {
        "id": st.id,
        "name": st.name,
        "faculty": st.faculty,
        "course": st.course,
        "grade": st.grade
    }
    r.setex(cache_key, 60, json.dumps(result, ensure_ascii=False))
    return result

@router.put("/{student_id}")
def update_student(
    student_id: int,
    name: str = None,
    faculty: str = None,
    course: str = None,
    grade: float = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Обновить запись (не кэшируем).
    При обновлении стоит удалить из кэша конкретный ключ, чтобы не хранить старые данные.
    """
    repo = StudentRepository(db)
    updated = repo.update_student(student_id, name, faculty, course, grade)
    if not updated:
        raise HTTPException(status_code=404, detail="Student not found")

    # Инвалидируем кэш (read_student)
    r.delete(f"student_id:{student_id}")
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
    current_user=Depends(get_current_user),
):
    """
    Удалить запись (не кэшируем).
    Аналогично стоит удалить ключ из кэша.
    """
    repo = StudentRepository(db)
    success = repo.delete_student(student_id)
    if not success:
        raise HTTPException(status_code=404, detail="Student not found")

    # Удаляем кэш
    r.delete(f"student_id:{student_id}")
    return {"message": f"Student with id={student_id} deleted successfully."}
