from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Request, HTTPException
from starlette import status

from src.auth.utils import decode_access_token


class AccessTokenBearer(HTTPBearer):
    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> dict:
        creds = await super().__call__(request)

        token_data = decode_access_token(creds.credentials)
        if token_data is None:
            raise HTTPException(
                status_code=status.HTTP_403_UNAUTHORIZED
            )

        if token_data.get("refresh"):
            raise HTTPException(
                status_code=status.HTTP_403_UNAUTHORIZED,
                detail="Please provide the access token"
            )

        return token_data
