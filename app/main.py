import uvicorn

from fastapi import FastAPI
from app.routers import contact

def create_app() -> FastAPI:
    app = FastAPI(
        title="Contact Service",
        version="1.0.0",
        description="Сервис для сбора обращений абонентов"
    )

    app.include_router(contact.router, prefix="/contact", tags=["Contact"])

    return app

app = create_app()

if __name__ == '__main__':
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
