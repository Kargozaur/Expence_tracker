from datetime import datetime, timedelta, timezone
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Response,
)
from copy import deepcopy
from sqlalchemy.ext.asyncio import AsyncSession
from core.settings import settings
from auth.oauth import create_refresh_token, create_token
from utility.hash_password import hash_password, verify_password
from utility.hash_token import hash_refresh_token
from models.models import User, RefreshToken
from dependancies.user_dependancy import get_user
from schemas.schemas import LoginUser, CreateUser, Token
from database import get_db

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/signin", status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: CreateUser,
    db: AsyncSession = Depends(get_db),
) -> Response:
    user = await get_user(user_data.email, db)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )
    try:
        hashed_password: str = hash_password(user_data.password)
        user_data.password = hashed_password
        new_user = User(**user_data.model_dump())
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{e}",
        )
    return Response(status_code=status.HTTP_201_CREATED)


@router.post("/login", response_model=Token)
async def login(
    user_credential: LoginUser, db: AsyncSession = Depends(get_db)
):
    user: User | None = await get_user(user_credential.email, db)
    if not user or user.is_active is False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email doesn't exists",
        )
    hashed_password = user.password if user else None
    if not hashed_password:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User is not found",
        )
    if not verify_password(user_credential.password, hashed_password):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User is not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    uid = deepcopy(user.id)
    short_token: str = create_token(
        data={"sub": str(user.id), "email": user.email}
    )
    refresh_token: str = create_refresh_token(
        data={"sub": str(uid), "email": user.email}
    )
    try:
        new_refresh = RefreshToken(
            token=hash_refresh_token(refresh_token),
            user_id=user.id,
            expires_at=datetime.now(timezone.utc)
            + timedelta(minutes=settings.LONG_EXPIRE),
        )
        db.add(new_refresh)
        await db.commit()
        await db.refresh(new_refresh)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{e}",
        )

    return {
        "access_token": short_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }
