
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.user import UserRole
from app.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, db: Session):
        self.users = UserRepository(db)

    def get_profile(self, user_id: int):
        user = self.users.get_by_id(user_id)
        if not user:
            raise HTTPException(404, "User not found")
        return user

    def list_users(self):
        return self.users.list_users()

    def update_role(self, user_id: int, role: UserRole):
        user = self.get_profile(user_id)
        user.role = role
        return self.users.save(user)

    def update_status(self, user_id: int, is_active: bool):
        user = self.get_profile(user_id)
        user.is_active = is_active
        return self.users.save(user)
