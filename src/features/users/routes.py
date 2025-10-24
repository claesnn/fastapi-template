from fastapi import APIRouter, Depends, status

from features.common.pagination import PaginatedResponse, PaginationQuery

from .services import UserService, get_user_service
from .schemas.base import UserCreate, UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_create: UserCreate,
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.create(user_create)


@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.get(user_id)


@router.get("/", response_model=PaginatedResponse[UserRead])
async def list_users(
    pagination: PaginationQuery,
    user_service: UserService = Depends(get_user_service),
):
    users, total = await user_service.list(pagination)
    return {
        "items": users,
        "total": total,
        "page": pagination.page,
        "page_size": pagination.page_size,
    }


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.update(user_id, user_update)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
):
    await user_service.delete(user_id)
