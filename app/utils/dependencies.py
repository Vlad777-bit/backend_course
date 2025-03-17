from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from app.utils.db import get_db
from app.utils.token_manager import get_user_id_by_token
from app.repository.user_repository import UserRepository

def get_current_user(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """
    Считывает токен из заголовка Authorization: Bearer <token>,
    находит соответствующего пользователя.
    Если нет токена или пользователь не найден — 401.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")

    token = authorization.split(" ")[1]
    user_id = get_user_id_by_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    repo = UserRepository(db)
    user = repo.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user
