
from datetime import datetime, timezone

import jwt
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    hash_refresh_token,
    decode_token,
)
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository
from app.repositories.refresh_token_repository import (
    RefreshTokenRepository,
)
from app.schemas.user import UserRegister


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)
        self.tokens = RefreshTokenRepository(db)

    def register(self, data: UserRegister) -> User:
        if self.users.get_by_username(data.username):
            raise HTTPException(409, "Username already exists")
        if self.users.get_by_email(str(data.email)):
            raise HTTPException(409, "Email already exists")

        # Public registration must never accept a role from the client.
        return self.users.create(
            username=data.username,
            email=str(data.email),
            hashed_password=hash_password(data.password),
            role=UserRole.EMPLOYEE,
            is_active=True,
        )

    def login(self, username: str, password: str) -> dict:
        user = self.users.get_by_username(username)

        if not user or not verify_password(
            password, user.hashed_password
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(403, "Account is inactive")

        refresh, expiry = create_refresh_token(user.id)
        self.tokens.create(
            user_id=user.id,
            token_hash=hash_refresh_token(refresh),
            expires_at=expiry,
        )
        return self._response(user, refresh)

    def refresh(self, refresh_token: str) -> dict:
        try:
            payload = decode_token(refresh_token, "refresh")
            user_id = int(payload["sub"])
        except (jwt.InvalidTokenError, ValueError, KeyError, TypeError):
            raise HTTPException(401, "Invalid or expired refresh token")

        digest = hash_refresh_token(refresh_token)
        record = self.tokens.get_by_hash(digest)

        if (
            not record
            or record.revoked
            or record.user_id != user_id
        ):
            raise HTTPException(401, "Refresh token is invalid or revoked")

        expiry = record.expires_at
        if expiry.tzinfo is None:
            expired = expiry <= datetime.now(timezone.utc).replace(tzinfo=None)
        else:
            expired = expiry <= datetime.now(timezone.utc)

        if expired:
            raise HTTPException(401, "Refresh token has expired")

        user = self.users.get_by_id(user_id)
        if not user or not user.is_active:
            raise HTTPException(401, "User is unavailable")

        # Single-use rotation: the previous refresh token is revoked.
        self.tokens.revoke(record)
        new_refresh, new_expiry = create_refresh_token(user.id)
        self.tokens.create(
            user_id=user.id,
            token_hash=hash_refresh_token(new_refresh),
            expires_at=new_expiry,
        )
        return self._response(user, new_refresh)

    def logout(self, refresh_token: str) -> None:
        try:
            decode_token(refresh_token, "refresh")
        except jwt.InvalidTokenError:
            raise HTTPException(401, "Invalid or expired refresh token")

        record = self.tokens.get_by_hash(
            hash_refresh_token(refresh_token)
        )
        if not record or record.revoked:
            raise HTTPException(401, "Refresh token is invalid or revoked")

        self.tokens.revoke(record)

    @staticmethod
    def _response(user: User, refresh: str) -> dict:
        from app.core.config import settings

        return {
            "access_token": create_access_token(
                user.id, user.role.value
            ),
            "refresh_token": refresh,
            "token_type": "bearer",
            "expires_in": settings.access_token_expire_minutes * 60,
        }
