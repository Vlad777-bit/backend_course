from pydantic import BaseModel, Field
from typing import Optional

class StudentCreate(BaseModel):
    name: str = Field(..., example="Иван Иванов")
    faculty: str = Field(..., example="Факультет Математики")
    course: str = Field(..., example="Математика-1")
    grade: float = Field(..., example=45.0)

class StudentUpdate(BaseModel):
    name: Optional[str] = Field(None, example="Пётр Петров")
    faculty: Optional[str] = Field(None, example="Факультет Физики")
    course: Optional[str] = Field(None, example="Физика-2")
    grade: Optional[float] = Field(None, example=30.0)

class StudentOut(BaseModel):
    id: int
    name: str
    faculty: str
    course: str
    grade: float

    class Config:
        from_attributes = True
