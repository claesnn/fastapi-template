from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from features.common.query import BaseListQuery


class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None
    is_active: bool


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    full_name: str | None = None
    is_active: bool | None = None


class UserRead(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class UserSortField(str, Enum):
    id = "id"
    username = "username"
    email = "email"


class UserListParams(BaseListQuery):
    username: str | None = Field(default=None, min_length=1)
    email: str | None = Field(default=None, min_length=1)
    is_active: bool | None = Field(default=None)
    sort_by: UserSortField = Field(default=UserSortField.id)
