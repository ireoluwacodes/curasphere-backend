from fastapi import FastAPI
import src.core.database  # noqa: F401

from src.api.user.router import router as user_router
from src.api.auth.router import router as auth_router


app = FastAPI()

app.include_router(user_router, prefix="/users", tags=["users"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])


@app.get("/")
async def root():
    return {"message": "Hello World"}
