from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./students.db"  # Можно заменить на любую СУБД

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def get_db():
    """
    Функция-зависимость для FastAPI, отдающая объект сессии.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
