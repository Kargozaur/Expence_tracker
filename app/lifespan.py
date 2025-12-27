from sqlalchemy.ext.asyncio import async_sessionmaker
from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import engine
from repositories.category_repository import CategoryRepository
from repositories.currency_repository import CurrencyRepository


@asynccontextmanager
async def lifespan(app: FastAPI):
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)
    async_session = async_sessionmaker(engine)
    async with async_session() as session:
        cat_repo = CategoryRepository(session)
        cur_repo = CurrencyRepository(session)

        categories = await cat_repo.get_all()
        currencies = await cur_repo.get_all()

        app.state.category_map = {
            c.category_name: c.id for c in categories
        }
        app.state.currency_map = {c.code: c.id for c in currencies}
    yield
    await engine.dispose()
