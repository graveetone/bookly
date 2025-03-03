import datetime
import uuid
from typing import Optional

from pydantic import BaseModel, Field


class Book(BaseModel):
    uid: uuid.UUID
    title: str
    author: str
    publisher: str
    published_date: datetime.date
    page_count: int
    language: str
    created_at: datetime.datetime
    updated_at: datetime.datetime


class BookCreateModel(BaseModel):
    title: str
    author: str
    publisher: str
    published_date: str
    page_count: int
    language: str


class BookUpdateModel(BaseModel):
    title: str
    author: str
    publisher: str
    page_count: int
    language: str


# class BookUpdateModel(BaseModel):
#     title: Optional[str] = Field(None)
#     author: Optional[str] = Field(None)
#     publisher: Optional[str] = Field(None)
#     published_date: Optional[str] = Field(None)
#     page_count: Optional[int] = Field(None)
#     language: Optional[str] = Field(None)
