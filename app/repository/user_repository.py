from sqlalchemy.orm import Session
from app.models.user_models import User
from typing import Optional

class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_user(self, username: str, password_hash: str, role: str = "user") -> User:
        user = User(
            username=username,
            password_hash=password_hash,
            role=role
        )
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def get_user_by_username(self, username: str) -> Optional[User]:
        return (
            self.session.query(User)
            .filter(User.username == username)
            .first()
        )

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.session.query(User).filter(User.id == user_id).first()
