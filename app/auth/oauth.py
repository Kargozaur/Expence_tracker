from typing import Any
from fastapi import status, Depends, HTTPException
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from app.schemas.schemas import TokenPayload
from database import get_db
from models.models import User
from core.settings import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


def create_token(data: dict[str, Any]) -> str:
    to_encode = data.copy()
    expire: datetime | float = datetime.now() + timedelta(
        minutes=EXPIRE_MINUTES  # type: ignore
    )
    to_encode.update({"exp": expire})
    encoded: str = jwt.encode(
        claims=to_encode, key=SECRET_KEY, algorithm=ALGORITHM
    )
    return encoded


def verify_access_token(
    token: str, credential_exception: Exception
) -> TokenPayload:
    try:
        payload: dict[str, Any] = jwt.decode(
            token=token, key=SECRET_KEY, algorithms=ALGORITHM
        )
        id = payload.get("sub")
        if not id:
            raise credential_exception
        return TokenPayload(sub=id)
    except JWTError:
        raise credential_exception


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    credential_exception: Exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unathorized",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = verify_access_token(token, credential_exception)
    if not token_data.sub:
        raise credential_exception
    uid: int = int(token_data.sub)
    result = await db.execute(select(User).where(User.id == uid))
    user = result.scalar_one_or_none()
    if not user:
        raise credential_exception
    return user
