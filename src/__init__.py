from fastapi import FastAPI

from src.auth.routes import auth_router
from src.books.routes import book_router
from contextlib import asynccontextmanager

from src.db.main import init_db
from src.reviews.routes import reviews_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Server is starting")
    await init_db()

    yield

    print("Server has been stopped")

version = "v1"
app = FastAPI(
    version=version,
    title="Bookly",
    description="Rest API for a book review web service",
    lifespan=lifespan
)

app.include_router(book_router, prefix=f"/api/{version}/books")
app.include_router(auth_router, prefix=f"/api/{version}/auth")
app.include_router(reviews_router, prefix=f"/api/{version}/reviews")
