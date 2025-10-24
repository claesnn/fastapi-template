from pydantic import BaseModel, ConfigDict


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
