# app/utils/db.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./students.db"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def get_db():
    """
    Зависимость для FastAPI.
    Возвращает объект сессии, который закрывается после использования.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
