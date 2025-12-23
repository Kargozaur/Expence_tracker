from fastapi import status, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from schemas.schemas import TokenPayload
from database import get_db
from models.models import User
from core.settings import settings
from core.errors import InvalidTokenError

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="login", auto_error=False
)


def verify_access_token(
    token: str, credential_exception: Exception
) -> TokenPayload:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        return TokenPayload(**payload)
    except InvalidTokenError:
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
    user = await db.get(User, uid)
    if not user:
        raise credential_exception
    return user
