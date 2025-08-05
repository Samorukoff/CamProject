from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from project.core.config.database.connection import get_db
from project.subscribe.repositories import update_subscription_statuses
import asyncio

def start_subscription_scheduler():
    scheduler = AsyncIOScheduler()

    @scheduler.scheduled_job(IntervalTrigger(minutes=10))
    async def update_task():
        async with get_db() as db:
            await update_subscription_statuses(db)

    scheduler.start()