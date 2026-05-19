from fastapi import APIRouter, Depends, Header
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.session import get_session
from app.schemas.auth_schema import LoginRequest, RegisterRequest, RefreshRequest, TokenResponse
from app.core.security import create_access_token
from app.services.auth_service import (
    authenticate_user,
    register_user,
    create_refresh_token,
    validate_refresh_token,
    invalidate_refresh_token,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=TokenResponse)
async def register(payload: RegisterRequest, session: AsyncSession = Depends(get_session)):
    user = await register_user(session, payload.email, payload.password, payload.full_name)
    tokens = await issue_tokens_with_rotation(session, user.id)
    return TokenResponse(**tokens)


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, session: AsyncSession = Depends(get_session)):
    user = await authenticate_user(session, payload.email, payload.password)
    tokens = await issue_tokens_with_rotation(session, user.id)
    return TokenResponse(**tokens)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(payload: RefreshRequest, session: AsyncSession = Depends(get_session)):
    user_id = await validate_refresh_token(session, payload.refresh_token)
    await invalidate_refresh_token(session, payload.refresh_token)
    tokens = await issue_tokens_with_rotation(session, user_id)
    return TokenResponse(**tokens)


async def issue_tokens_with_rotation(session: AsyncSession, user_id: str) -> dict:
    subject = str(user_id)
    access = create_access_token(subject)
    refresh = await create_refresh_token(session, subject)
    return {"access_token": access, "refresh_token": refresh}
