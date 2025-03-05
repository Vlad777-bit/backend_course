import uvicorn

from fastapi import FastAPI
from app.models.student_models import Base as StudentBase
from app.models.user_models import Base as UserBase
from app.utils.db import engine
from app.routers import student, auth

def create_app() -> FastAPI:
    app = FastAPI(title="My Service with Auth")

    # Создаём таблицы
    StudentBase.metadata.create_all(bind=engine)
    UserBase.metadata.create_all(bind=engine)

    # Подключаем роутеры
    app.include_router(auth.router, prefix="/auth", tags=["Auth"])
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
