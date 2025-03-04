from fastapi.security import HTTPBearer
from fastapi import Request, HTTPException, status

from src.auth.utils import decode_access_token


class TokenBearer(HTTPBearer):
    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> dict:
        creds = await super().__call__(request)

        token_data = decode_access_token(creds.credentials)
        if token_data is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN
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
