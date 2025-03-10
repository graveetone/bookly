from typing import Any, Callable

from fastapi.requests import Request
from fastapi.responses import JSONResponse


class BooklyException(Exception):
    ...


class InvalidTokenException(BooklyException):
    ...


class RevokedTokenException(BooklyException):
    ...


class AccessTokenRequiredException(BooklyException):
    ...


class RefreshTokenRequiredException(BooklyException):
    ...


class UserAlreadyExistsException(BooklyException):
    ...


class InsufficientPermissionsException(BooklyException):
    ...


class BookNotFoundException(BooklyException):
    ...


class InvalidCredentialsException(BooklyException):
    ...

class UserNotFoundException(BooklyException):
    ...

class AccountNotVerifiedException(BooklyException):
    ...


class PasswordNotMatchException(BooklyException):
    ...

def create_exception_handler(status_code: int, detail: Any) -> Callable[[Request, Exception], JSONResponse]:
    async def exception_handler(request: Request, exception: BooklyException) -> JSONResponse:
        return JSONResponse(
            content=detail,
            status_code=status_code,
        )

    return exception_handler


EXCEPTIONS_MAP = {
    InvalidTokenException: dict(
        status_code=401,
        detail={
            "message": "Invalid or expired token provided",
            "error_code": "invalid_token"
        }
    ),
    RevokedTokenException: dict(
        status_code=401,
        detail={
            "message": "Revoked token provided",
            "error_code": "revoked_token"
        }
    ),
    AccessTokenRequiredException: dict(
        status_code=401,
        detail={
            "message": "Access token required",
            "error_code": "access_token_required"
        }
    ),
    RefreshTokenRequiredException: dict(
        status_code=401,
        detail={
            "message": "Refresh token required",
            "error_code": "refresh_token_required"
        }
    ),
    UserAlreadyExistsException: dict(
        status_code=400,
        detail={
            "message": "User with email already exists",
            "error_code": "user_already_exists"
        }
    ),
    InsufficientPermissionsException: dict(
        status_code=403,
        detail={
            "message": "Permission denied",
            "error_code": "permission_denied"
        }
    ),
    BookNotFoundException: dict(
        status_code=404,
        detail={
            "message": "Book not found",
            "error_code": "book_not_found"
        }
    ),
    InvalidCredentialsException: dict(
        status_code=401,
        detail={
            "message": "Invalid credentials",
            "error_code": "invalid_credentials"
        }
    ),
    UserNotFoundException: dict(
        status_code=404,
        detail={
            "message": "User not found",
            "error_code": "user_not_found",
        }
    ),
    AccountNotVerifiedException: dict(
        status_code=403,
        detail={
            "message": "Account not yet verified",
            "error_code": "account_not_verified",
            "resolution": "Please check your email for verification details"
        }
    ),
    PasswordNotMatchException: dict(
        status_code=400,
        detail={
            "message": "Passwords do not match",
            "error_code": "password_not_match",
            "resolution": "Please check your password and confirmation password are the same"
        }
    )
}
