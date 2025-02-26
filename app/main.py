import uvicorn

from fastapi import FastAPI
from app.routers.student import router as student_router
from app.models.student_models import Base
from app.utils.db import engine

def create_app() -> FastAPI:
    app = FastAPI(title="My App", version="1.0.0")

    # 1. Создаём таблицы на основе наших моделей
    Base.metadata.create_all(bind=engine)

    # 2. Подключаем роутеры
    app.include_router(student_router, prefix="/student", tags=["Student"])

    return app

app = create_app()


if __name__ == '__main__':
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
