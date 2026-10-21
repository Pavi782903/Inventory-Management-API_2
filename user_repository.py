
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int):
        return self.db.get(User, user_id)

    def get_by_username(self, username: str):
        return self.db.scalar(
            select(User).where(User.username == username)
        )

    def get_by_email(self, email: str):
        return self.db.scalar(
            select(User).where(User.email == email)
        )

    def list_users(self):
        return list(
            self.db.scalars(select(User).order_by(User.id)).all()
        )

    def create(self, **values):
        user = User(**values)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def save(self, user: User):
        self.db.commit()
        self.db.refresh(user)
        return user
