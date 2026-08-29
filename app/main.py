from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import create_tables
from app.models import User
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(users_router, prefix="/users", tags=["users"])

