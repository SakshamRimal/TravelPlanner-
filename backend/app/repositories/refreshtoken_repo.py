from datetime import datetime

from passlib.context import CryptContext
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refreshtoken_model import RefreshToken

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class RefreshTokenRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, user_id: str, token: str, expires_at: datetime) -> RefreshToken:
        token_hash = pwd_context.hash(token)
        refresh_token = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        self.session.add(refresh_token)
        await self.session.commit()
        await self.session.refresh(refresh_token)
        return refresh_token

    async def find_valid_token(self, user_id: str, token: str) -> RefreshToken | None:
        result = await self.session.execute(
            select(RefreshToken).where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked == False,
                RefreshToken.expires_at > datetime.utcnow(),
            )
        )
        token_record = result.scalar_one_or_none()
        if token_record and pwd_context.verify(token, token_record.token_hash):
            return token_record
        return None

    async def revoke(self, token_record: RefreshToken) -> None:
        token_record.revoked = True
        await self.session.commit()

    async def revoke_all_for_user(self, user_id: str) -> None:
        result = await self.session.execute(
            select(RefreshToken).where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked == False,
            )
        )
        tokens = result.scalars().all()
        for token in tokens:
            token.revoked = True
        await self.session.commit()