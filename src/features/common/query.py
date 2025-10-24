from enum import Enum

from pydantic import Field

from .pagination import PaginationParams


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"


class BaseListQuery(PaginationParams):
    sort_order: SortOrder = Field(default=SortOrder.asc)
