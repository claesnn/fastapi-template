from structlog import configure, get_logger, make_filtering_bound_logger
from structlog.contextvars import merge_contextvars
from structlog.processors import JSONRenderer, TimeStamper
from settings import settings


configure(
    wrapper_class=make_filtering_bound_logger(min_level=settings.log_level),
    processors=[
        merge_contextvars,
        TimeStamper(fmt="iso"),
        JSONRenderer(),
    ],
)

logger = get_logger("app_logger")
