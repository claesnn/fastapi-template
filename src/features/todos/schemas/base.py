from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from features.common.query import BaseListQuery


class TodoBase(BaseModel):
    title: str
    description: str | None = None
    completed: bool
    user_id: int | None = None


class TodoCreate(TodoBase):
    pass


class TodoUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None
    user_id: int | None = None


class TodoRead(TodoBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class TodoSortField(str, Enum):
    id = "id"
    title = "title"
    completed = "completed"
    user_id = "user_id"


class TodoListParams(BaseListQuery):
    completed: bool | None = Field(default=None)
    user_id: int | None = Field(default=None, ge=1)
    sort_by: TodoSortField = Field(default=TodoSortField.id)
