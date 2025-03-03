import datetime

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.books.models import Book
from src.books.schemas import BookCreateModel, BookUpdateModel




class BookService:
    async def get_all_books(self, session: AsyncSession):
        statement = select(Book).order_by(Book.created_at)
        result = await session.exec(statement)
        return result.all()

    async def get_book(self, book_uid: str, session: AsyncSession):
        statement = select(Book).where(Book.uid == book_uid)
        result = await session.exec(statement)
        return result.first()

    async def create_book(self, book_data: BookCreateModel, session: AsyncSession):
        book_data_dict = book_data.model_dump()
        book = Book(**book_data_dict)
        book.published_date = datetime.datetime.strptime(book_data_dict["published_date"], "%Y-%m-%d")
        session.add(book)
        await session.commit()

        return book

    async def update_book(self, book_uid: str, book_data: BookUpdateModel, session: AsyncSession):
        book = await self.get_book(book_uid, session)
        if book is None:
            return book

        book_data_dict = book_data.model_dump()
        book_data_dict["updated_at"] = datetime.datetime.now()
        for k, v in book_data_dict.items():
            setattr(book, k, v)

        await session.commit()
        return book

    async def delete_book(self, book_uid: str, session: AsyncSession):
        book = await self.get_book(book_uid, session)
        if book is None:
            return book

        await session.delete(book)
        await session.commit()
