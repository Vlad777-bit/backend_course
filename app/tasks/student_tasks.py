from app.utils.db import SessionLocal
from app.repository.student_repository import StudentRepository
from app.utils.redis_client import r

def import_csv_task(csv_path: str):
    """
    Фоновая задача для импорта CSV в БД.
    """
    db = SessionLocal()
    try:
        repo = StudentRepository(db)
        repo.insert_students_from_csv(csv_path)
        # После изменения БД желательно сбросить кэш
        r.flushdb()
        print(f"[TASK] Импорт завершён для файла: {csv_path}")
    finally:
        db.close()

def delete_students_task(ids: list[int]):
    """
    Фоновая задача для удаления записей по списку ID.
    """
    db = SessionLocal()
    try:
        repo = StudentRepository(db)
        repo.delete_students_by_ids(ids)
         # Сбрасываем кэш
        r.flushdb()
        print(f"[TASK] Удалены студенты с id {ids}")
    finally:
        db.close()
