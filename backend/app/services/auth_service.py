from datetime import datetime, timedelta

from fastapi import Depends, Header, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    create_refresh_token as create_refresh_token_jwt,
    get_password_hash,
    verify_password,
)
from app.db.session import get_session
from app.models.user_model import User
from app.repositories.refreshtoken_repo import RefreshTokenRepository
from app.repositories.user_repo import UserRepository
from app.utils.errors import UnauthorizedError


def _decode_token(token: str) -> dict:
    settings = get_settings()
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise UnauthorizedError("Invalid token") from exc


async def get_current_user(
    session: AsyncSession = Depends(get_session),
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> User:
    if not authorization:
        raise UnauthorizedError("Missing token")

    token = authorization.replace("Bearer ", "")
    payload = _decode_token(token)
    if payload.get("type") != "access":
        raise UnauthorizedError("Invalid token type")

    user_id = payload.get("sub")
    repo = UserRepository(session)
    user = await repo.get_by_id(user_id)
    if not user:
        raise UnauthorizedError("User not found")
    return user


async def register_user(session: AsyncSession, email: str, password: str, full_name: str | None):
    repo = UserRepository(session)
    existing = await repo.get_by_email(email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    user = User(email=email, full_name=full_name, hashed_password=get_password_hash(password))
    return await repo.add(user)


async def authenticate_user(session: AsyncSession, email: str, password: str):
    repo = UserRepository(session)
    user = await repo.get_by_email(email)
    if not user or not verify_password(password, user.hashed_password):
        raise UnauthorizedError("Invalid credentials")
    return user


def issue_tokens(user: User) -> dict:
    access = create_access_token(str(user.id))
    refresh = create_refresh_token_jwt(str(user.id))
    return {"access_token": access, "refresh_token": refresh}


async def create_refresh_token(session: AsyncSession, user_id: str) -> str:
    token = create_refresh_token_jwt(user_id)
    settings = get_settings()
    expires_at = datetime.utcnow() + timedelta(days=settings.refresh_token_expires_days)
    repo = RefreshTokenRepository(session)
    await repo.create(user_id, token, expires_at)
    return token


async def validate_refresh_token(session: AsyncSession, token: str) -> str:
    payload = _decode_token(token)
    if payload.get("type") != "refresh":
        raise UnauthorizedError("Invalid refresh token")
    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedError("Invalid refresh token")
    repo = RefreshTokenRepository(session)
    token_record = await repo.find_valid_token(user_id, token)
    if not token_record:
        raise UnauthorizedError("Refresh token has been revoked or is invalid")
    return user_id


async def invalidate_refresh_token(session: AsyncSession, token: str) -> None:
    payload = _decode_token(token)
    user_id = payload.get("sub")
    if not user_id:
        return
    repo = RefreshTokenRepository(session)
    token_record = await repo.find_valid_token(user_id, token)
    if token_record:
        await repo.revoke(token_record)
