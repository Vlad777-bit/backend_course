from fastapi import APIRouter, HTTPException # type: ignore

router = APIRouter()

@router.get("/add")
def add(a: float, b: float):
    """Возвращает сумму a + b"""
    return {"result": a + b}

@router.get("/subtract")
def subtract(a: float, b: float):
    """Возвращает разность a - b"""
    return {"result": a - b}

@router.get("/multiply")
def multiply(a: float, b: float):
    """Возвращает произведение a * b"""
    return {"result": a * b}

@router.get("/divide")
def divide(a: float, b: float):
    """Возвращает частное a / b. Проверяет деление на ноль."""
    if b == 0:
        raise HTTPException(status_code=400, detail="Деление на ноль невозможно")
    return {"result": a / b}
