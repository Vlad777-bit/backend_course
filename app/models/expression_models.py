from pydantic import BaseModel # type: ignore

class ExpressionComponent(BaseModel):
    a: float
    op: str
    b: float
    join_op: str = None

class FullExpression(BaseModel):
    expr: str  # Полное арифметическое выражение, например, "(1+2)*3 + (4-5)/(6-7)"
