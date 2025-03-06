from fastapi import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import status

from src.auth.service import UserService
from src.books.service import BookService
from src.db.models import Review
from src.reviews.schemas import ReviewCreateModel

book_service = BookService()
user_service = UserService()


class ReviewService:
    async def create_review(self, user_email: str, book_uid: str, review: ReviewCreateModel, session: AsyncSession):
        try:
            book = await book_service.get_book(book_uid=book_uid, session=session)
            user = await user_service.get_user_by_email(email=user_email, session=session)

            review_data = review.model_dump()

            review = Review(**review_data)

            breakpoint()
            if not book:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Book not found",
                )
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )

            review.user = user
            review.book = book

            session.add(review)
            await session.commit()

            return review
        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=500,
                detail="Something went wrong"
            )
