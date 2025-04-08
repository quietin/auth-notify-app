# app/main.py

# load different configs according to different environment
from dotenv import load_dotenv
import os

if os.getenv("APP_ENV") == "docker":
    load_dotenv(".env.docker")
else:
    load_dotenv(".env.local")

import logging

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import init_db
from app.logger import init_logging
from contextlib import asynccontextmanager
from app.api import user
from app.config import BASE_DIR


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize resources before FastAPI starts
    init_db()
    init_logging()

    yield

    # Clean up resources after FastAPI shuts down (if needed)


logger = logging.getLogger(__name__)


app = FastAPI(lifespan=lifespan)
app.mount(
    "/static",
    StaticFiles(directory=os.path.join(BASE_DIR, "static")),
    name="static"
)
app.include_router(user.router, prefix="")
