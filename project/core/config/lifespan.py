from contextlib import asynccontextmanager
from fastapi import FastAPI
from project.core.config.database.connection import engine
from project.core.base.models import Base
from project.subscribe.utils.scheduler import start_subscription_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Инициализация базы данных
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Старт фона (например, APScheduler)
    start_subscription_scheduler()

    yield