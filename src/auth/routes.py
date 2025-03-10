import datetime
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.responses import JSONResponse
from starlette import status

from src.auth.dependencies import RefreshTokenBearer, AccessTokenBearer, get_current_user, RoleChecker
from src.auth.schemas import UserCreateModel, UserCreatedModel, UserLoginModel, UserBooksModel, EmailModel, \
    PasswordResetRequestModel, PasswordResetConfirmModel
from src.auth.service import UserService
from src.auth.utils import create_access_token, decode_access_token, verify_password, create_url_safe_token, \
    decode_url_safe_token
from src.celery_tasks import send_email
from src.config import Config
from src.db.main import get_session
from src.db.redis import add_jti_to_blocklist
from src.errors import UserAlreadyExistsException, InvalidCredentialsException, InvalidTokenException, \
    UserNotFoundException, PasswordNotMatchException


auth_router = APIRouter(tags=["auth"])
user_service = UserService()

REFRESH_TOKEN_EXPIRY = timedelta(days=2)
access_token_bearer = AccessTokenBearer()
refresh_token_bearer = RefreshTokenBearer()
admin_role_checker = RoleChecker(allowed_roles=["ADMIN"])


@auth_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def create_user_account(
        user_data: UserCreateModel,
        bg_tasks: BackgroundTasks,
        session: AsyncSession = Depends(get_session),
):
    email = user_data.email
    user_exists = await user_service.user_exists(email=email, session=session)

    if user_exists:
        raise UserAlreadyExistsException()

    user = await user_service.create_user(
        user_data=user_data,
        session=session
    )

    token = create_url_safe_token({"email": email})
    link = f"http://{Config.DOMAIN}/api/v1/auth/verify/{token}"

    html = f"""
    <h1>Verify your email, {user.first_name}</h1>
    <p>Please click this <a href="{link}">link</a> to verify your email</p>
    """

    send_email.delay(
        recipients=[email],
        subject="Verify your account",
        body=html,
    )

    return {
        "message": "Account created! Check email to verify",
        "user": user
    }


@auth_router.get("/verify/{token}", status_code=status.HTTP_200_OK)
async def verify_user_account(token: str, session: AsyncSession = Depends(get_session)):
    email = decode_url_safe_token(token).get("email")
    if not email:
        return JSONResponse(content={
            "message": "Error occurred during verification"
        }, status_code=500)

    user = await user_service.get_user_by_email(email, session=session)
    if not user:
        raise UserNotFoundException

    await user_service.update_user(user, {"is_verified": True}, session=session)

    return JSONResponse(content={
        "message": "Account verified successfully",
    }, status_code=200)


@auth_router.post("/login", status_code=status.HTTP_200_OK)
async def login(user_data: UserLoginModel, session: AsyncSession = Depends(get_session)):
    email = user_data.email
    password = user_data.password

    user = await user_service.get_user_by_email(email, session=session)

    if user is None or not verify_password(password, user.password_hash):
        raise InvalidCredentialsException()

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
        raise InvalidTokenException()

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


@auth_router.get("/me", response_model=UserBooksModel)
async def get_current_user(current_user = Depends(get_current_user), _=Depends(admin_role_checker)):
    return current_user


@auth_router.post("/send_mail")
async def send_mail(emails: EmailModel):
    send_email.delay(
        recipients=emails.addresses,
        subject="Welcome to Bookly",
        body="<h1>Welcome to the Bookly app</h1>",
    )

    return {
        "message": "Email sent successfully!"
    }


@auth_router.post("/password-reset")
async def password_reset(email_data: PasswordResetRequestModel, session: AsyncSession = Depends(get_session)):

    token = create_url_safe_token({"email": email_data.email})
    link = f"http://{Config.DOMAIN}/api/v1/auth/confirm-reset-password/{token}"

    send_email.delay(
        recipients=[email_data.email],
        subject="Reset your password",
        body=f"<h1>Click this <a href='{link}'>link</a> to reset your password</h1>",
    )

    return JSONResponse(content={
        "message": "Please check your email for instruction to reset your password!"
    }, status_code=200)


@auth_router.post("/confirm-reset-password/{token}", status_code=status.HTTP_200_OK)
async def reset_account_password(token: str, password_reset_data: PasswordResetConfirmModel, session: AsyncSession = Depends(get_session)):
    if password_reset_data.new_password != password_reset_data.confirm_password:
        raise PasswordNotMatchException

    email = decode_url_safe_token(token).get("email")
    if not email:
        return JSONResponse(content={
            "message": "Error occurred during verification"
        }, status_code=500)

    user = await user_service.get_user_by_email(email, session=session)
    if not user:
        raise UserNotFoundException

    await user_service.update_user(user, {"password": password_reset_data.new_password}, session=session)

    return JSONResponse(content={
        "message": "Password was reset!",
    }, status_code=200)
