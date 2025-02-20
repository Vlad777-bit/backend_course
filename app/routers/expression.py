from fastapi import APIRouter, HTTPException # type: ignore
from app.models.expression_models import ExpressionComponent, FullExpression
from app.utils.safe_eval import safe_eval

router = APIRouter()

# Глобальная переменная для хранения текущего выражения
current_expression = ""

@router.get("/get")
def get_expression():
    """
    Возвращает текущее накопленное выражение.
    Если выражение не задано, возвращается соответствующее сообщение.
    """
    if not current_expression:
        return {"expression": None, "message": "Выражение не задано"}
    return {"expression": current_expression}

@router.post("/component")
def add_expression_component(component: ExpressionComponent):
    """
    Добавляет компонент (например, (a op b)) в текущее выражение.
    Если выражение пустое, то записывает его как первый компонент.
    Если выражение уже задано, объединяет через join_op (по умолчанию используется '+').
    """
    global current_expression

    # Проверка допустимости оператора
    if component.op not in ["+", "-", "*", "/"]:
        raise HTTPException(
            status_code=400,
            detail="Оператор компонента должен быть одним из: '+', '-', '*', '/'"
        )
    if component.join_op is not None and component.join_op not in ["+", "-", "*", "/"]:
        raise HTTPException(
            status_code=400,
            detail="Оператор объединения (join_op) должен быть одним из: '+', '-', '*', '/'"
        )

    comp_str = f"({component.a} {component.op} {component.b})"
    if not current_expression:
        current_expression = comp_str
    else:
        join_op = component.join_op if component.join_op is not None else "+"
        # Оборачиваем текущее выражение в скобки для сохранения приоритета операций
        current_expression = f"({current_expression}) {join_op} {comp_str}"

    return {"expression": current_expression}

@router.post("/full")
def set_full_expression(full_expr: FullExpression):
    """
    Устанавливает полное выражение, переданное в теле запроса, и возвращает результат его вычисления.
    Пример запроса:
    {
       "expr": "(1+2)*3 + (4-5)/(6-7)"
    }
    """
    global current_expression
    current_expression = full_expr.expr
    try:
        result = safe_eval(current_expression)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка вычисления: {e}")
    return {"expression": current_expression, "result": result}

@router.post("/evaluate")
def evaluate_current_expression():
    """
    Вычисляет текущее накопленное выражение и возвращает результат.
    Если выражение не задано, возвращает ошибку.
    """
    if not current_expression:
        raise HTTPException(status_code=400, detail="Выражение не задано")
    try:
        result = safe_eval(current_expression)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка вычисления: {e}")
    return {"expression": current_expression, "result": result}
