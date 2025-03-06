from datetime import datetime, date
from typing import Optional

import sqlalchemy.dialects.postgresql as pg
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column
import uuid
from src.auth import models


class Book(SQLModel, table=True):
    __tablename__ = "books"

    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    title: str
    author: str
    published_date: date
    publisher: str
    page_count: int
    language: str
    user_uid: Optional[uuid.UUID] = Field(default=None, foreign_key="users.uid")
    user: Optional["models.User"] = Relationship(back_populates="books")
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))

    def __repr__(self):
        return f"<Book {self.title}>"
