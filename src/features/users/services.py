from .models import User
from .schemas.base import UserCreate, UserUpdate
from database import get_db
from fastapi import Depends, HTTPException
from features.common.pagination import PaginationParams
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_create: UserCreate) -> User:
        """Create a new user."""
        user = User(**user_create.model_dump())
        self.db.add(user)

        try:
            await self.db.commit()
        except IntegrityError:
            raise HTTPException(
                status_code=400, detail="Username or email already exists"
            )

        return user

    async def get(self, user_id: int) -> User:
        user = await self.db.get(User, user_id)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return user

    async def list(self, pagination: PaginationParams) -> tuple[list[User], int]:
        total = await self.db.scalar(select(func.count()).select_from(User)) or 0
        query = (
            select(User)
            .order_by(User.id)
            .offset(pagination.offset)
            .limit(pagination.page_size)
        )
        result = await self.db.scalars(query)
        users = list(result)
        return users, int(total)

    async def update(self, user_id: int, user_update: UserUpdate) -> User:
        user = await self.get(user_id)

        for field, value in user_update.model_dump(exclude_unset=True).items():
            setattr(user, field, value)

        self.db.add(user)

        try:
            await self.db.commit()
        except IntegrityError:
            raise HTTPException(
                status_code=400, detail="Username or email already exists"
            )

        return user

    async def delete(self, user_id: int) -> None:
        """Delete a user."""
        user = await self.get(user_id)

        await self.db.delete(user)
        await self.db.commit()


async def get_user_service(
    db: AsyncSession = Depends(get_db),
) -> UserService:
    return UserService(db)
