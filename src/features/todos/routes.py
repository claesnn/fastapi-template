from fastapi import APIRouter, Depends, status

from features.common.pagination import PaginatedResponse, PaginationQuery
from features.todos.schemas.relational import TodoReadWithUser
from .services import TodoService, get_todo_service
from .schemas.base import TodoCreate, TodoRead, TodoUpdate

router = APIRouter(prefix="/todos", tags=["todos"])


@router.post("/", response_model=TodoRead, status_code=status.HTTP_201_CREATED)
async def create_todo(
    todo_create: TodoCreate,
    todo_service: TodoService = Depends(get_todo_service),
):
    return await todo_service.create(todo_create)


@router.get("/with-users", response_model=PaginatedResponse[TodoReadWithUser])
async def list_todos_with_users(
    pagination: PaginationQuery,
    todo_service: TodoService = Depends(get_todo_service),
):
    todos, total = await todo_service.list_with_users(pagination)
    return {
        "items": todos,
        "total": total,
        "page": pagination.page,
        "page_size": pagination.page_size,
    }


@router.get("/{todo_id}", response_model=TodoRead)
async def get_todo(
    todo_id: int,
    todo_service: TodoService = Depends(get_todo_service),
):
    return await todo_service.get(todo_id)


@router.get("/", response_model=PaginatedResponse[TodoRead])
async def list_todos(
    pagination: PaginationQuery,
    todo_service: TodoService = Depends(get_todo_service),
):
    todos, total = await todo_service.list(pagination)
    return {
        "items": todos,
        "total": total,
        "page": pagination.page,
        "page_size": pagination.page_size,
    }


@router.patch("/{todo_id}", response_model=TodoRead)
async def update_todo(
    todo_id: int,
    todo_update: TodoUpdate,
    todo_service: TodoService = Depends(get_todo_service),
):
    return await todo_service.update(todo_id, todo_update)


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    todo_id: int,
    todo_service: TodoService = Depends(get_todo_service),
):
    await todo_service.delete(todo_id)
