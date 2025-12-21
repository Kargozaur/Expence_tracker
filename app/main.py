from fastapi import FastAPI
from database import engine
from contextlib import asynccontextmanager
from models.models import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)


@app.get("/")
def main():
    print("Hello from expence-tracker!")


if __name__ == "__main__":
    main()
