from fastapi import APIRouter, Depends

from app.schemas.user_schema import UserRead
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserRead)
async def me(user=Depends(get_current_user)):
    return UserRead(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        created_at=user.created_at,
    )
