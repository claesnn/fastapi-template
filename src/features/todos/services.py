from .models import Todo
from .schemas.base import TodoCreate, TodoListParams, TodoSortField, TodoUpdate
from database import get_db
from fastapi import Depends, HTTPException
from features.common.query import SortOrder
from features.users.services import UserService, get_user_service
from logger import logger
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


class TodoService:

    def __init__(self, db: AsyncSession, user_service: UserService):
        self.db = db
        self.user_service = user_service

    async def create(self, todo_create: TodoCreate, *, flush: bool = True) -> Todo:
        """Create a new todo item."""
        if todo_create.user_id is not None:
            # Verify that the user exists
            await self.user_service.get(todo_create.user_id)

        todo = Todo(**todo_create.model_dump())
        self.db.add(todo)
        if flush:
            await self.db.flush()
        await logger.ainfo(f"Created todo item with id {todo.id}", todo_id=todo.id)
        return todo

    async def get(self, todo_id: int) -> Todo:
        todo = await self.db.get(Todo, todo_id)

        if not todo:
            raise HTTPException(status_code=404, detail="Todo not found")

        return todo

    async def list(
        self, params: TodoListParams, include_user: bool = False
    ) -> tuple[list[Todo], int]:
        filters = self._filters(params)

        count_stmt = select(func.count()).select_from(Todo)
        if filters:
            count_stmt = count_stmt.where(*filters)
        total = int(await self.db.scalar(count_stmt) or 0)

        stmt = select(Todo)
        if include_user:
            stmt = stmt.options(selectinload(Todo.user))
        if filters:
            stmt = stmt.where(*filters)
        stmt = stmt.order_by(self._ordering_column(params))
        stmt = stmt.offset(params.offset).limit(params.page_size)

        todos = list(await self.db.scalars(stmt))
        return todos, total

    async def list_with_users(
        self, params: TodoListParams
    ) -> tuple[list[Todo], int]:
        return await self.list(params, include_user=True)

    async def update(
        self, todo_id: int, todo_update: TodoUpdate, *, flush: bool = False
    ) -> Todo:
        todo = await self.get(todo_id)

        for field, value in todo_update.model_dump(exclude_unset=True).items():
            setattr(todo, field, value)

        self.db.add(todo)
        if flush:
            await self.db.flush()

        return todo

    async def delete(self, todo_id: int) -> None:
        """Delete a todo item."""
        todo = await self.get(todo_id)

        await self.db.delete(todo)

    def _filters(self, params: TodoListParams) -> list:
        clauses = []
        if params.completed is not None:
            clauses.append(Todo.completed == params.completed)
        if params.user_id is not None:
            clauses.append(Todo.user_id == params.user_id)
        return clauses

    def _ordering_column(self, params: TodoListParams):
        match params.sort_by:
            case TodoSortField.title:
                column = Todo.title
            case TodoSortField.completed:
                column = Todo.completed
            case TodoSortField.user_id:
                column = Todo.user_id
            case _:
                column = Todo.id

        if params.sort_order == SortOrder.desc:
            return column.desc()
        return column.asc()


async def get_todo_service(
    db: AsyncSession = Depends(get_db),
    user_service: UserService = Depends(get_user_service),
) -> TodoService:
    return TodoService(db, user_service)
