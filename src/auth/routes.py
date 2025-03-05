import datetime
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.responses import JSONResponse
from starlette import status

from src.auth.dependencies import RefreshTokenBearer, AccessTokenBearer, get_current_user, RoleChecker
from src.auth.schemas import UserCreateModel, UserCreatedModel, UserLoginModel
from src.auth.service import UserService
from src.auth.utils import create_access_token, decode_access_token, verify_password
from src.db.main import get_session
from src.db.redis import add_jti_to_blocklist

auth_router = APIRouter(tags=["auth"])
user_service = UserService()

REFRESH_TOKEN_EXPIRY = timedelta(days=2)
access_token_bearer = AccessTokenBearer()
refresh_token_bearer = RefreshTokenBearer()
admin_role_checker = RoleChecker(allowed_roles=["ADMIN"])


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


@auth_router.post("/login", status_code=status.HTTP_200_OK)
async def login(user_data: UserLoginModel, session: AsyncSession = Depends(get_session)):
    email = user_data.email
    password = user_data.password

    user = await user_service.get_user_by_email(email, session=session)

    if user is None or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    access_token = create_access_token(
        user_data={
            "email": email,
            "user_uid": str(user.uid),
        }
    )
    refresh_token = create_access_token(
        user_data={
            "email": email,
            "user_uid": str(user.uid),
        },
        refresh=True,
        expiry=REFRESH_TOKEN_EXPIRY
    )

    return JSONResponse(content={
        "message": "Logged in successfully",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {
            "email": email,
            "uid": str(user.uid),
            "role": user.role
        }
    })


@auth_router.get("/refresh_token")
async def get_new_access_token(token_details: dict = Depends(refresh_token_bearer)):
    expiry_timestamp = token_details.get("exp")
    if datetime.datetime.fromtimestamp(expiry_timestamp) <= datetime.datetime.now():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")

    new_access_token = create_access_token(
        user_data = token_details["user"]
    )
    return JSONResponse(content={
        "access_token": new_access_token
    })


@auth_router.delete("/logout")
async def logout(token_details: dict = Depends(access_token_bearer)):
    await add_jti_to_blocklist(token_details["jti"])
    return JSONResponse({
        "message": "Token was revoked",
    })


@auth_router.get("/me")
async def get_current_user(current_user = Depends(get_current_user), _=Depends(admin_role_checker)):
    return current_user
