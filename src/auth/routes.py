from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status

from src.auth.schemas import UserCreateModel, UserCreatedModel
from src.auth.service import UserService
from src.db.main import get_session

auth_router = APIRouter(tags=["auth"])
user_service = UserService()


@auth_router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=UserCreatedModel)
async def create_user_account(user_data: UserCreateModel, session: AsyncSession = Depends(get_session)):
    email = user_data.email
    user_exists = await user_service.user_exists(email=email, session=session)

    if user_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"User with email {email} already exists")

    user = await user_service.create_user(
        user_data=user_data,
        session=session
    )

    return user
