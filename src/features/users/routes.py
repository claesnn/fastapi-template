from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from features.common.pagination import PaginatedResponse, paginate

from .services import UserService, get_user_service
from .schemas.base import UserCreate, UserListParams, UserRead, UserUpdate

UserListQuery = Annotated[UserListParams, Query()]

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_create: UserCreate,
    db: AsyncSession = Depends(get_db),
    user_service: UserService = Depends(get_user_service),
):
    async with db.begin():
        user = await user_service.create(user_create)
    return user


@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.get(user_id)


@router.get("/", response_model=PaginatedResponse[UserRead])
async def list_users(
    pagination: UserListQuery,
    user_service: UserService = Depends(get_user_service),
):
    users, total = await user_service.list(pagination)
    return paginate(users, total, pagination)


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db),
    user_service: UserService = Depends(get_user_service),
):
    async with db.begin():
        user = await user_service.update(user_id, user_update)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    user_service: UserService = Depends(get_user_service),
):
    async with db.begin():
        await user_service.delete(user_id)
