from fastapi import APIRouter, Depends, Response, status
from services.user_service import UserService
from schemas.schemas import CreateUser, LoginUser
from dependancies.user.user_router_dependancy import (
    get_user_service,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/signin", status_code=201, response_model=None)
async def create_user(
    user: CreateUser,
    user_service: UserService = Depends(get_user_service),
):
    await user_service.create_user(user)
    return Response(status_code=status.HTTP_201_CREATED)


@router.post("/login")
async def login_user(
    user_credential: LoginUser,
    user_service: UserService = Depends(get_user_service),
):
    await user_service.login_user(user_credential)
