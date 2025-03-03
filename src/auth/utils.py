import logging
import uuid
from datetime import timedelta, datetime

import jwt
from passlib.context import CryptContext

from src.config import Config

password_context = CryptContext(
    schemes=["bcrypt"]
)

ACCESS_TOKEN_EXPIRY = 60 * 60


def generate_password_hash(password: str) -> str:
    return password_context.hash(password)


def verify_password(password: str, hash: str) -> bool:
    return password_context.verify(secret=password, hash=hash)


def create_access_token(user_data: dict, expiry: timedelta = None, refresh: bool = False):
    expiry = expiry or timedelta(seconds=ACCESS_TOKEN_EXPIRY)

    payload = {
        "user": user_data,
        "exp": datetime.now() + expiry,
        "jti": str(uuid.uuid4()),
        "refresh": refresh,
    }

    return jwt.encode(
        payload=payload,
        key=Config.JWT_SECRET_KEY,
        algorithm=Config.JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(
            jwt=token,
            key=Config.JWT_SECRET_KEY,
            algorithms=[Config.JWT_ALGORITHM],
        )
    except jwt.PyJWTError as error:
        logging.exception(error)
