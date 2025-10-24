from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from settings import settings

engine = create_async_engine(
    settings.db_url, echo=settings.db_echo, pool_size=settings.db_pool_size
)
local_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    async with local_session() as session:
        yield session


class Base(DeclarativeBase):
    pass
