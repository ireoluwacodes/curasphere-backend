from fastapi import FastAPI
import src.database

from src.api.user.router import router as user_router


app = FastAPI()

app.include_router(user_router, prefix="/users", tags=["users"])


@app.get("/")
async def root():
    return {"message": "Hello World"}
