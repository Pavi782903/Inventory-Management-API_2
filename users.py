
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, admin_required
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import (
    UserResponse, RoleUpdate, StatusUpdate,
)
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def get_me(user: User = Depends(get_current_user)):
    return user


@router.get("", response_model=list[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    _: User = Depends(admin_required),
):
    return UserService(db).list_users()


@router.patch("/{user_id}/role", response_model=UserResponse)
def update_role(
    user_id: int,
    data: RoleUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(admin_required),
):
    if user_id == admin.id and data.role != admin.role:
        from fastapi import HTTPException
        raise HTTPException(
            400, "Use another administrator to change your role"
        )
    return UserService(db).update_role(user_id, data.role)


@router.patch("/{user_id}/status", response_model=UserResponse)
def update_status(
    user_id: int,
    data: StatusUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(admin_required),
):
    if user_id == admin.id and not data.is_active:
        from fastapi import HTTPException
        raise HTTPException(
            400, "You cannot deactivate your own account"
        )
    return UserService(db).update_status(user_id, data.is_active)
