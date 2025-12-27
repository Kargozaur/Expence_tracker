from services.token_service import ITokenService
from repositories.token_repository import ITokenRepository
from models.models import User
from schemas.schemas import CreateUser, LoginUser
from repositories.user_repository import (
    IUserRepository,
)
from repositories.password_repository import (
    IPasswordHasher,
)
from core.errors import (
    UserDoesntExist,
    UserAlreadyExists,
    WrongCredentials,
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
        """Data validation when creating user"""
        if not user_data.email or not user_data.password:
            raise WrongCredentials

    async def check_user_exists(self, email: str) -> None:
        """
        Method to check if user email is in db when trying to create a new one
        Raises:
            UserAlreadyExists: _description_
        """
        existing_user: (
            User | None
        ) = await self.user_repository.get_user_by_email(email)
        if existing_user:
            raise UserAlreadyExists

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
        """
        Right now the main problem with the authorization handling is that
        user can create multiple tockens. Solution to that is to check the device
        (to dodge the collisions between mobile's/laptops/tablets/etc.).
        I'm not sure should I do it inside not so complex project.

        Raises:
            UserDoesntExist: _description_
            WrongCredentials: _description_

        """
        user = await self.user_repository.get_user_by_email(
            user_data.email
        )
        if not user:
            raise UserDoesntExist

        if not self.password_repository.verify_password(
            user_data.password, user.password
        ):
            raise WrongCredentials

        await self.token_repository.revoke_token(user.id)
        access_token: str = self.token_service.create_token(user)
        refresh_token, expires_at = (
            self.token_service.create_refresh_token(user)
        )

        await self.token_repository.save(
            user.id,
            refresh_token,
            expires_at=expires_at,
        )
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    async def logout_user(self, user_id):
        """If front-end is done, revokes token, setting expire_date at db to datetime.now()"""
        await self.token_repository.revoke_token(user_id)
