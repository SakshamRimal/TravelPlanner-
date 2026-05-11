from fastapi import APIRouter, Depends, Header
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.session import get_session
from app.schemas.auth import LoginRequest, RegisterRequest, RefreshRequest, TokenResponse
from app.core.security import create_access_token
from app.services.auth import authenticate_user, issue_tokens, register_user, validate_refresh_token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=TokenResponse)
async def register(payload: RegisterRequest, session: AsyncSession = Depends(get_session)):
    user = await register_user(session, payload.email, payload.password, payload.full_name)
    tokens = issue_tokens(user)
    return TokenResponse(**tokens)


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, session: AsyncSession = Depends(get_session)):
    user = await authenticate_user(session, payload.email, payload.password)
    tokens = issue_tokens(user)
    return TokenResponse(**tokens)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(payload: RefreshRequest):
    user_id = validate_refresh_token(payload.refresh_token)
    access = create_access_token(user_id)
    return TokenResponse(access_token=access, refresh_token=payload.refresh_token)
