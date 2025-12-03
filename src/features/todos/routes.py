from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from features.common.pagination import PaginatedResponse, paginate
from .services import TodoService, get_todo_service
from .schemas.base import (
    TodoCreate,
    TodoExpandField,
    TodoListParams,
    TodoRead,
    TodoUpdate,
)
from features.todos.schemas.relational import TodoReadFull

TodoListQuery = Annotated[TodoListParams, Query()]

router = APIRouter(prefix="/todos", tags=["todos"])


@router.post("/", response_model=TodoRead, status_code=status.HTTP_201_CREATED)
async def create_todo(
    todo_create: TodoCreate,
    db: AsyncSession = Depends(get_db),
    todo_service: TodoService = Depends(get_todo_service),
):
    async with db.begin():
        todo = await todo_service.create(todo_create)
    return todo


@router.get("/{todo_id}", response_model=TodoReadFull)
async def get_todo(
    todo_id: int,
    todo_service: TodoService = Depends(get_todo_service),
):
    return await todo_service.get(todo_id)


@router.get("/", response_model=PaginatedResponse[TodoReadFull])
async def list_todos(
    params: TodoListQuery,
    todo_service: TodoService = Depends(get_todo_service),
):
    include_user = TodoExpandField.user in params.expand
    todos, total = await todo_service.list(params, include_user=include_user)
    return paginate(todos, total, params)


@router.patch("/{todo_id}", response_model=TodoRead)
async def update_todo(
    todo_id: int,
    todo_update: TodoUpdate,
    db: AsyncSession = Depends(get_db),
    todo_service: TodoService = Depends(get_todo_service),
):
    async with db.begin():
        todo = await todo_service.update(todo_id, todo_update)
    return todo


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    todo_id: int,
    db: AsyncSession = Depends(get_db),
    todo_service: TodoService = Depends(get_todo_service),
):
    async with db.begin():
        await todo_service.delete(todo_id)
