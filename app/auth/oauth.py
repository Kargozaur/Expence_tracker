from fastapi import status, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer
from database import get_db
from models.models import User

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="login", auto_error=False
)


def verify_access_token(
    self, token: str, credential_exception: Exception
) -> TokenPayload:
    try:
        payload: dict[str, Any] = jwt.decode(
            token=token,
            key=self.secret_key,
            algorithms=self.algorithm,
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
