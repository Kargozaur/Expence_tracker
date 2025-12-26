from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
)
from services.user_service import UserService
from schemas.schemas import CreateUser, LoginUser
from dependancies.user.user_router_dependancy import (
    get_user_service,
)
from core.errors import (
    UserDoesntExist,
    UserAlreadyExists,
    WrongCredentials,
)
from auth.oauth import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/signup", status_code=201, response_model=None)
async def create_user(
    user: CreateUser,
    user_service: UserService = Depends(get_user_service),
):
    try:
        await user_service.create_user(user)
        return Response(status_code=status.HTTP_201_CREATED)
    except UserAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exist",
        )


@router.post("/login")
async def login_user(
    user_credential: LoginUser,
    user_service: UserService = Depends(get_user_service),
):
    try:
        user = await user_service.login_user(user_credential)
        return user
    except UserDoesntExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User Does not exist",
        )
    except WrongCredentials:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Email or password is not correct",
        )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logour_user(
    current_user=Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    await user_service.logout_user(current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
