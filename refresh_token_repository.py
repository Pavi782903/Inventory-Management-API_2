
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.refresh_token import RefreshToken


class RefreshTokenRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_hash(self, token_hash: str):
        return self.db.scalar(
            select(RefreshToken).where(
                RefreshToken.token_hash == token_hash
            )
        )

    def create(self, user_id: int, token_hash: str, expires_at):
        record = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
            revoked=False,
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def revoke(self, record: RefreshToken):
        record.revoked = True
        self.db.commit()
