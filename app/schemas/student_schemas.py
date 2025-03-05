from pydantic import BaseModel, Field
from typing import Optional

class StudentCreate(BaseModel):
    name: str = Field(..., json_schema_extra="Иван Иванов")
    faculty: str = Field(..., json_schema_extra="Факультет Математики")
    course: str = Field(..., json_schema_extra="Математика-1")
    grade: float = Field(..., json_schema_extra=45.0)

class StudentUpdate(BaseModel):
    name: Optional[str] = Field(None, json_schema_extra="Пётр Петров")
    faculty: Optional[str] = Field(None, json_schema_extra="Факультет Физики")
    course: Optional[str] = Field(None, json_schema_extra="Физика-2")
    grade: Optional[float] = Field(None, json_schema_extra=30.0)

class StudentOut(BaseModel):
    id: int
    name: str
    faculty: str
    course: str
    grade: float

    class Config:
        from_attributes = True
