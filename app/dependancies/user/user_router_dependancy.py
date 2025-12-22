from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from services.token_service import TokenService
from database import get_db
from repositories.user_dependancy import UserRepository
from repositories.password_dependancy import PasswordHasher
from repositories.token_dependancy import TokenRepository
from services.user_service import UserService
from core.settings import Settings


async def get_user_repository(
    db: AsyncSession = Depends(get_db),
) -> UserRepository:
    return UserRepository(db)


async def get_password_hasher() -> PasswordHasher:
    return PasswordHasher()


async def get_password_repository(
    password: PasswordHasher = Depends(get_password_hasher),
):
    return password


async def get_token_repository(
    db: AsyncSession = Depends(get_db),
) -> TokenRepository:
    return TokenRepository(db)


async def get_settings() -> Settings:
    return Settings()  # type: ignore


async def get_token_service(
    settings: Settings = Depends(get_settings),
) -> TokenService:
    return TokenService(settings)


async def get_user_service(
    repo: UserRepository = Depends(get_user_repository),
    password: PasswordHasher = Depends(get_password_repository),
    token_db: TokenRepository = Depends(get_token_repository),
    token_service: TokenService = Depends(get_token_service),
) -> UserService:
    return UserService(repo, password, token_db, token_service)
