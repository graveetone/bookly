from sqlmodel import create_engine, SQLModel
from sqlalchemy.ext.asyncio import AsyncEngine
from src.config import Config

from src.books.models import Book


engine = AsyncEngine(
    create_engine(
        url=Config.DATABASE_URL,
        echo=True
    )
)


async def init_db():
    async with engine.begin() as connection:
        # this will use metadata of SQLModel and create all inherited models
        await connection.run_sync(SQLModel.metadata.create_all)
