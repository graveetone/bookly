from typing import List, Optional

from fastapi import HTTPException, APIRouter
from starlette import status

from src.books.data import books
from src.books.schemas import Book, BookUpdateModel

book_router = APIRouter(tags=["books"])


@book_router.get("/", response_model=List[Book])
async def get_all_books() -> list:
    return books


@book_router.post("/", response_model=Book, status_code=status.HTTP_201_CREATED)
async def create_book(book: Book) -> Book:
    books.append(book)
    return book


@book_router.get("/{book_id}")
async def get_book(book_id: int) -> Optional[Book]:
    book = next(iter([book for book in books if book.get("id") == book_id]), None)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id '{book_id}' not found"
        )
    return Book(**book)


@book_router.patch("/{book_id}")
async def update_book(book_id: int, data: BookUpdateModel) -> Book:
    book = next(iter([book for book in books if book.get("id") == book_id]), None)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id '{book_id}' not found"
        )

    book.update(data.dict(exclude_unset=True))
    book = Book(**book)
    return book


@book_router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int):
    book = next(iter([book for book in books if book.get("id") == book_id]), None)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id '{book_id}' not found"
        )

    books.remove(book)
