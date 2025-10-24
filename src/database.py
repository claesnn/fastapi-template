from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from settings import settings

engine_kwargs = {"echo": settings.db_echo}
if make_url(settings.db_url).get_backend_name() != "sqlite":
    engine_kwargs["pool_size"] = settings.db_pool_size

engine = create_async_engine(settings.db_url, **engine_kwargs)
local_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    async with local_session() as session:
        yield session


class Base(DeclarativeBase):
    pass
