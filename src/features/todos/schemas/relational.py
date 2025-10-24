from .base import TodoRead
from features.users.schemas.base import UserRead


class TodoReadWithUser(TodoRead):
    user: UserRead | None = None
