import ast
from fastapi import HTTPException # type: ignore

def safe_eval(expr: str) -> float:
    """
    Безопасно вычисляет арифметическое выражение, содержащее операции +, -, *, / и скобки.
    """
    try:
        node = ast.parse(expr, mode='eval')
        return _eval(node.body)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка при вычислении выражения: {e}")

def _eval(node):
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        else:
            raise TypeError("Неподдерживаемый тип константы")
    elif isinstance(node, ast.BinOp):
        left = _eval(node.left)
        right = _eval(node.right)
        if isinstance(node.op, ast.Add):
            return left + right
        elif isinstance(node.op, ast.Sub):
            return left - right
        elif isinstance(node.op, ast.Mult):
            return left * right
        elif isinstance(node.op, ast.Div):
            if right == 0:
                raise ZeroDivisionError("Деление на ноль")
            return left / right
        else:
            raise TypeError("Неподдерживаемый бинарный оператор")
    elif isinstance(node, ast.UnaryOp):
        operand = _eval(node.operand)
        if isinstance(node.op, ast.UAdd):
            return +operand
        elif isinstance(node.op, ast.USub):
            return -operand
        else:
            raise TypeError("Неподдерживаемый унарный оператор")
    else:
        raise TypeError("Неподдерживаемый тип выражения")
