from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from core.settings import settings

SQL_ALCHEMY_URL = settings.DATABASE_URL

engine = create_async_engine(
    url=SQL_ALCHEMY_URL, max_overflow=10, future=True
)

AsyncSessionLocal = sessionmaker(
    bing=engine, class_=AsyncSession, autoflush=False
)


async def get_db():  # type: ignore
    async with AsyncSessionLocal() as session:  # type: ignore
        try:
            yield session
        finally:
            await session.close()  # type: ignore
