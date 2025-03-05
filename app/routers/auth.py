from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from passlib.hash import bcrypt

from app.repository.user_repository import UserRepository
from app.utils.db import get_db
from app.utils.token_manager import create_token_for_user, get_user_id_by_token, delete_token
from app.schemas.auth_schemas import UserRegister, UserLogin, UserOut, TokenOut

router = APIRouter()

@router.post("/register", response_model=UserOut)
def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    repo = UserRepository(db)
    existing = repo.get_user_by_username(user_data.username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    # Хэшируем пароль (passlib + bcrypt)
    password_hash = bcrypt.hash(user_data.password)
    new_user = repo.create_user(
        username=user_data.username,
        password_hash=password_hash,
        role=user_data.role
    )
    return new_user  # Pydantic преобразует User -> UserOut

@router.post("/login", response_model=TokenOut)
def login_user(credentials: UserLogin, db: Session = Depends(get_db)):
    repo = UserRepository(db)
    user = repo.get_user_by_username(credentials.username)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    # Проверяем пароль
    if not bcrypt.verify(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Создаём токен
    token = create_token_for_user(user.id)
    return TokenOut(access_token=token)

@router.post("/logout")
def logout_user(authorization: str = Header(None)):
    """
    Ожидаем заголовок Authorization: Bearer <token>
    Удаляем токен из in_memory_tokens
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    token = authorization.split(" ")[1]
    delete_token(token)
    return {"message": "Successfully logged out"}
