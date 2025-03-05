from fastapi.security import HTTPBearer
from fastapi import Request, HTTPException, status, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.service import UserService
from src.auth.utils import decode_access_token
from src.db.main import get_session
from src.db.redis import jti_in_blocklist


class TokenBearer(HTTPBearer):
    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> dict:
        creds = await super().__call__(request)

        token_data = decode_access_token(creds.credentials)
        if token_data is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "The token is invalid or expired",
                    "resolution": "Please get new token",
                }
            )
        if await jti_in_blocklist(jti=token_data["jti"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "The token is invalid or revoked",
                    "resolution": "Please get new token",
                }
            )
        self.verify_token_data(token_data=token_data)

        return token_data

    def verify_token_data(self, token_data):
        raise NotImplementedError("TokenBearer does not implements verify_token_data")


class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict):
        if token_data and token_data.get("refresh"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please provide the access token"
            )


class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict):
        if token_data and token_data.get("refresh") is None:
            raise HTTPException(
                status_code=status.HTTP_403_UNAUTHORIZED,
                detail="Please provide the refresh token"
            )


async def get_current_user(
        token_details: dict = Depends(AccessTokenBearer()),
        session: AsyncSession = Depends(get_session)
):
    user_email = token_details["user"]["email"]
    return await UserService().get_user_by_email(email=user_email, session=session)


class RoleChecker:
    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles

    async def __call__(self, current_user = Depends(get_current_user)):
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to perform this action"
            )
