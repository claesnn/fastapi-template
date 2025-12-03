from .base import TodoRead
from features.users.schemas.base import UserRead


class TodoReadFull(TodoRead):
    user: UserRead | None = None
