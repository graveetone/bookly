from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.dependencies import get_current_user
from src.auth.schemas import UserCreatedModel
from src.db.main import get_session
from src.reviews.schemas import ReviewCreateModel, ReviewModel
from src.reviews.service import ReviewService

reviews_router = APIRouter(tags=["review"])

review_service = ReviewService()


@reviews_router.post("/book/{book_uid}", response_model=ReviewModel)
async def create_review(
        book_uid: str,
        review_data: ReviewCreateModel,
        current_user: UserCreatedModel = Depends(get_current_user),
        session: AsyncSession = Depends(get_session)
):
    review = await review_service.create_review(
        book_uid=book_uid,
        user_email=current_user.email,
        review=review_data,
        session=session
    )

    return review
