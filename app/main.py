import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import users, expenses
from lifespan import lifespan

app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,  # ty:ignore[invalid-argument-type]
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(users.router)
app.include_router(expenses.router)


@app.get("/")
def main():
    print("Hello from expence-tracker!")


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=7000, reload=True)
