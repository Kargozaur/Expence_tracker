from core.settings import Settings
from typing import Any
from datetime import datetime, timedelta
from jose import jwt
from abc import ABC, abstractmethod
from models.models import User


class ITokenService(ABC):
    @abstractmethod
    def create_token(self, user: User) -> str:
        pass

    @abstractmethod
    def create_refresh_token(
        self, user: User
    ) -> tuple[str, datetime]:
        pass


class TokenService(ITokenService):
    def __init__(self, settings: Settings):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.access_ttl = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_ttl = settings.LONG_EXPIRE

    def create_token(self, user: User) -> str:
        to_encode: dict[str, Any] = {"sub": str(user.id)}
        expire: datetime | float = datetime.now() + timedelta(
            minutes=self.access_ttl  # type: ignore
        )
        to_encode.update({"exp": expire})
        encoded: str = jwt.encode(
            claims=to_encode,
            key=self.secret_key,
            algorithm=self.algorithm,
        )
        return encoded

    def create_refresh_token(
        self, user: User
    ) -> tuple[str, datetime]:
        to_encode: dict[str, Any] = {"sub": str(user.id)}
        expire: datetime | float = datetime.now() + timedelta(
            minutes=self.refresh_ttl  # type: ignore
        )
        to_encode.update({"exp": expire})
        encoded: str = jwt.encode(
            claims=to_encode,
            key=self.secret_key,
            algorithm=self.algorithm,
        )
        return encoded, expire
