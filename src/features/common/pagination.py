from typing import Annotated, Generic, Sequence, TypeVar, TypedDict

from fastapi import Query
from pydantic import BaseModel, Field

T = TypeVar("T")

DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


class PaginationParams(BaseModel):
    page: int = Field(1, ge=1)
    page_size: int = Field(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    total: int
    page: int
    page_size: int
    items: list[T]


PaginationQuery = Annotated[PaginationParams, Query()]


class PaginatedPayload(TypedDict, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int


def paginate(
    items: Sequence[T], total: int, pagination: PaginationParams
) -> PaginatedPayload[T]:
    return {
        "items": list(items),
        "total": total,
        "page": pagination.page,
        "page_size": pagination.page_size,
    }
