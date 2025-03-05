import uvicorn

from fastapi import FastAPI
from app.models.student_models import Base
from app.utils.db import engine
from app.routers import student

def create_app() -> FastAPI:
    app = FastAPI(title="Student Service", version="1.0.0")

    # Создаём таблицу 'students' в БД, если её нет
    Base.metadata.create_all(bind=engine)

    # Подключаем роутер /student
    app.include_router(student.router, prefix="/student", tags=["Student"])

    return app

app = create_app()


if __name__ == '__main__':
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
