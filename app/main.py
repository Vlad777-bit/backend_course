import uvicorn # type: ignore

from fastapi import FastAPI # type: ignore
from app.routers import calculator, expression

app = FastAPI(title="Калькулятор FastAPI")

# Подключаем роутеры с префиксами и тегами для документации
app.include_router(
    calculator.router,
    prefix="/calculator",
    tags=["Calculator"],
)
app.include_router(
    expression.router,
    prefix="/expression",
    tags=["Expression"]
)

if __name__ == '__main__':
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
