import os
import logging.config
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from fastapi import FastAPI
from contextlib import asynccontextmanager
from typing import Annotated
from fastapi.params import Depends
from dotenv import load_dotenv

from .models import Base

load_dotenv()


user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
database = os.getenv("POSTGRES_DATABASE")

async_engine = create_async_engine(
    f"postgresql+asyncpg://{user}:{password}@localhost:5432/{database}"
)
async_session = async_sessionmaker(async_engine, expire_on_commit=False)


@asynccontextmanager
async def lifespan(apps: FastAPI):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield


async def get_session():
    async with async_session() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]

LOGLEVEL = os.getenv("LOG_LEVEL")

logging.config.dictConfig({
    "version": 1,
    "disable_existing_logger": False,
    "formatters": {
        "console": {
            "format": "%(asctime)s %(levelname)s [%(name)s:%(lineno)s] %(module)s %(message)s"
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "console",
        },
    },
    "loggers": {
        "": {
            "level": LOGLEVEL,
            "handlers": [
                "console",
            ]
        }
    }
})

