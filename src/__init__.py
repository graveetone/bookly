from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from src.auth.routes import auth_router
from src.books.routes import book_router
from contextlib import asynccontextmanager

from src.db.main import init_db
from src.reviews.routes import reviews_router
from src.errors import EXCEPTIONS_MAP, create_exception_handler


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

for exception, info in EXCEPTIONS_MAP.items():
    app.add_exception_handler(
        exception,
        create_exception_handler(
            status_code=info['status_code'],
            detail=info["detail"]
        )
    )


@app.exception_handler(500)
async def internal_server_error_handler(request: Request, exception: Exception) -> JSONResponse:
    return JSONResponse(
        content={
            "message": "Something went wrong",
            "error_code": "internal_server_error"
        }, status_code=500
    )
