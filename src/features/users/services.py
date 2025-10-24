from .models import User
from .schemas.base import UserCreate, UserListParams, UserSortField, UserUpdate
from database import get_db
from fastapi import Depends, HTTPException
from features.common.query import SortOrder
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.elements import ColumnElement


class UserService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_create: UserCreate, *, flush: bool = True) -> User:
        """Create a new user."""
        user = User(**user_create.model_dump())
        self.db.add(user)

        try:
            if flush:
                await self.db.flush()
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

    async def list(self, params: UserListParams) -> tuple[list[User], int]:
        filters = self._filters(params)

        count_stmt = select(func.count()).select_from(User)
        if filters:
            count_stmt = count_stmt.where(*filters)
        total = int(await self.db.scalar(count_stmt) or 0)

        stmt = select(User)
        if filters:
            stmt = stmt.where(*filters)
        stmt = stmt.order_by(self._ordering_column(params))
        stmt = stmt.offset(params.offset).limit(params.page_size)

        users = list(await self.db.scalars(stmt))
        return users, total

    async def update(
        self, user_id: int, user_update: UserUpdate, *, flush: bool = True
    ) -> User:
        user = await self.get(user_id)

        for field, value in user_update.model_dump(exclude_unset=True).items():
            setattr(user, field, value)

        self.db.add(user)

        try:
            if flush:
                await self.db.flush()
        except IntegrityError:
            raise HTTPException(
                status_code=400, detail="Username or email already exists"
            )

        return user

    async def delete(self, user_id: int) -> None:
        """Delete a user."""
        user = await self.get(user_id)

        await self.db.delete(user)

    def _filters(self, params: UserListParams) -> list[ColumnElement[bool]]:
        clauses: list[ColumnElement[bool]] = []
        if params.username:
            clauses.append(
                func.lower(User.username).like(self._normalize_like(params.username))
            )
        if params.email:
            clauses.append(
                func.lower(User.email).like(self._normalize_like(params.email))
            )
        if params.is_active is not None:
            clauses.append(User.is_active == params.is_active)
        return clauses

    def _ordering_column(self, params: UserListParams):
        if params.sort_by == UserSortField.username:
            column = User.username
        elif params.sort_by == UserSortField.email:
            column = User.email
        else:
            column = User.id
        if params.sort_order == SortOrder.desc:
            return column.desc()
        return column.asc()

    @staticmethod
    def _normalize_like(value: str) -> str:
        return f"%{value.lower()}%"


async def get_user_service(
    db: AsyncSession = Depends(get_db),
) -> UserService:
    return UserService(db)
