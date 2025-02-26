from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Float

Base = declarative_base()

class Student(Base):
    """
    Модель таблицы 'students' с полями:
      - id (PK)
      - name (ФИО студента)
      - faculty (название факультета)
      - course (название курса)
      - grade (оценка, float)
    """
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    faculty = Column(String(100), nullable=False)
    course = Column(String(100), nullable=False)
    grade = Column(Float, nullable=False)
