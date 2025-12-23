from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
from contextlib import asynccontextmanager
from models.models import Base
from routers import users


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(users.router)


@app.get("/")
def main():
    print("Hello from expence-tracker!")


if __name__ == "__main__":
    main()
