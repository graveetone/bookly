from typing import List, Optional

from fastapi import HTTPException, APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status

from src.auth.dependencies import AccessTokenBearer, RoleChecker
from src.books.schemas import Book, BookUpdateModel, BookCreateModel
from src.books.service import BookService
from src.db.main import get_session


book_router = APIRouter(
    tags=["books"],
    dependencies=[
        Depends(RoleChecker(allowed_roles=["ADMIN"]))
    ]
)
book_service = BookService()
access_token_bearer = AccessTokenBearer()

@book_router.get("/", response_model=List[Book])
async def get_all_books(session: AsyncSession = Depends(get_session), user_details: AccessTokenBearer = Depends(access_token_bearer)) -> list:
    return await book_service.get_all_books(session)


@book_router.post("/", response_model=Book, status_code=status.HTTP_201_CREATED)
async def create_book(book: BookCreateModel, session: AsyncSession = Depends(get_session), user_details: AccessTokenBearer = Depends(access_token_bearer)) -> Book:
    return await book_service.create_book(book, session)


@book_router.get("/{book_uid}", response_model=Book)
async def get_book(book_uid: str, session: AsyncSession = Depends(get_session), user_details: AccessTokenBearer = Depends(access_token_bearer)) -> Optional[Book]:
    book = await book_service.get_book(book_uid, session)
    if book:
        return book

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Book with id '{book_uid}' not found"
    )


@book_router.patch("/{book_uid}", response_model=Book)
async def update_book(book_uid: str, data: BookUpdateModel, session: AsyncSession = Depends(get_session), user_details: AccessTokenBearer = Depends(access_token_bearer)) -> Book:
    book = await book_service.update_book(book_uid, data, session)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id '{book_uid}' not found"
        )

    return book


@book_router.delete("/{book_uid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_uid: str, session: AsyncSession = Depends(get_session), user_details: AccessTokenBearer = Depends(access_token_bearer)):
    await book_service.delete_book(book_uid, session)
