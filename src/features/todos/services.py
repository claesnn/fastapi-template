from .models import Todo
from .schemas.base import TodoCreate, TodoUpdate
from database import get_db
from fastapi import Depends, HTTPException
from features.common.pagination import PaginationParams
from features.users.services import UserService, get_user_service
from logger import logger
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


class TodoService:
    def __init__(self, db: AsyncSession, userService: UserService):
        self.db = db
        self.userService = userService

    async def create(self, todo_create: TodoCreate) -> Todo:
        """Create a new todo item."""
        if todo_create.user_id is not None:
            # Verify that the user exists
            await self.userService.get(todo_create.user_id)

        todo = Todo(**todo_create.model_dump())
        self.db.add(todo)
        await self.db.commit()
        await logger.ainfo(f"Created todo item with id {todo.id}", todo_id=todo.id)
        return todo

    async def get(self, todo_id: int) -> Todo:
        todo = await self.db.get(Todo, todo_id)

        if not todo:
            raise HTTPException(status_code=404, detail="Todo not found")

        return todo

    async def list(self, pagination: PaginationParams) -> tuple[list[Todo], int]:
        total = await self.db.scalar(select(func.count()).select_from(Todo)) or 0
        query = (
            select(Todo)
            .order_by(Todo.id)
            .offset(pagination.offset)
            .limit(pagination.page_size)
        )
        result = await self.db.scalars(query)
        todos = list(result)
        return todos, int(total)

    async def list_with_users(
        self, pagination: PaginationParams
    ) -> tuple[list[Todo], int]:
        total = await self.db.scalar(select(func.count()).select_from(Todo)) or 0
        query = (
            select(Todo)
            .options(selectinload(Todo.user))
            .order_by(Todo.id)
            .offset(pagination.offset)
            .limit(pagination.page_size)
        )
        result = await self.db.scalars(query)
        todos = list(result)
        return todos, int(total)

    async def update(self, todo_id: int, todo_update: TodoUpdate) -> Todo:
        todo = await self.get(todo_id)

        for field, value in todo_update.model_dump(exclude_unset=True).items():
            setattr(todo, field, value)

        self.db.add(todo)
        await self.db.commit()

        return todo

    async def delete(self, todo_id: int) -> None:
        """Delete a todo item."""
        todo = await self.get(todo_id)

        await self.db.delete(todo)
        await self.db.commit()


async def get_todo_service(
    db: AsyncSession = Depends(get_db),
    user_service: UserService = Depends(get_user_service),
) -> TodoService:
    return TodoService(db, user_service)
