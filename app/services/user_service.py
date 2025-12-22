from fastapi import HTTPException, status
from services.token_service import ITokenService
from repositories.token_dependancy import ITokenRepository
from models.models import User
from schemas.schemas import CreateUser, LoginUser
from repositories.user_dependancy import (
    IUserRepository,
)
from repositories.password_dependancy import (
    IPasswordHasher,
)


class UserService:
    def __init__(
        self,
        user_repository: IUserRepository,
        password_repository: IPasswordHasher,
        token_repository: ITokenRepository,
        token_service: ITokenService,
    ):
        self.user_repository = user_repository
        self.password_repository = password_repository
        self.token_repository = token_repository
        self.token_service = token_service

    async def validate_user_data(self, user_data: CreateUser):
        if not user_data.email or not user_data.password:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT
            )

    async def check_user_exists(self, email: str) -> None:
        existing_user = await self.user_repository.get_user_by_email(
            email
        )
        if existing_user:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT)

    async def create_user(self, user_data: CreateUser) -> User:
        await self.validate_user_data(user_data)
        await self.check_user_exists(user_data.email)
        user: User = User(
            password=self.password_repository.hash_password(
                user_data.password
            ),
            email=user_data.email,
        )
        new_user: User = await self.user_repository.add_user(user)
        return new_user

    async def login_user(self, user_data: LoginUser):
        user = await self.user_repository.get_user_by_email(
            user_data.email
        )
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        if not self.password_repository.verify_password(
            user_data.password, user.password
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED
            )

        access_token = self.token_service.create_token(user)
        refresh_token, expires_at = (
            self.token_service.create_refresh_token(user)
        )

        await self.token_repository.save(
            user.id, refresh_token, expires_at=expires_at
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
