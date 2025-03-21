from fastapi import FastAPI
import src.core.database  # noqa: F401
from fastapi.middleware.cors import CORSMiddleware
from src.api.user.router import router as user_router
from src.api.auth.router import router as auth_router
from src.api.appointment.router import router as appointment_router
from src.api.sse.service import setup_sse_routes


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(
    appointment_router, prefix="/appointment", tags=["appointment"]
)
app.include_router(user_router, prefix="/users", tags=["users"])

# Setup SSE routes
setup_sse_routes(app)


@app.get("/")
async def root():
    return {"message": "Hello World"}
