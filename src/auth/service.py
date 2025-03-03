from sqlmodel import select

from src.auth.models import User
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.schemas import UserCreateModel
from src.auth.utils import generate_password_hash


class UserService:
    async def create_user(self, user_data: UserCreateModel, session: AsyncSession) -> User:
        user_data_dict = user_data.model_dump()
        user = User(
            **user_data_dict,
            password_hash=generate_password_hash(user_data_dict["password"])
        )

        session.add(user)
        await session.commit()

        return user

    async def get_user_by_email(self, email: str, session: AsyncSession):
        statement = select(User).where(User.email == email)

        result = await session.exec(statement)

        return result.first()

    async def user_exists(self, email: str, session: AsyncSession):
        user = await self.get_user_by_email(email=email, session=session)

        return user is not None
