from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, update, insert
from project.subscribe.models import Subscription, SubscriptionType
from datetime import datetime, timedelta
from project.core.config.database.context import db_session_ctx

from project.core.config.logging.logger import logger

# Поиск подписки пользователя в БД
async def get_user_subscription(user_id: int) -> Subscription | None:
    db = db_session_ctx.get()
    logger.debug(f"Fetching active subscription for user_id={user_id}")

    stmt = (
        select(Subscription).where(
        Subscription.user_id == user_id,
        Subscription.is_active == True)
        .options(selectinload(Subscription.subscription_type))
    )
    result = await db.execute(stmt)
    subscription = result.scalars().first()

    if subscription:
        logger.info(f"Active subscription found for user_id={user_id}")
    else:
        logger.info(f"No active subscription found for user_id={user_id}")
    return subscription

# Создание подписки пользователя в БД
async def create_subscription_for_user(user_id: int, subscription_type_id: int):
    db = db_session_ctx.get()
    now = datetime.utcnow()
    subscription_data = {
        "user_id": user_id,
        "subscription_type_id": subscription_type_id,
        "start_date": now,
        "end_date": now + timedelta(days=30),
        "is_active": False,
    }
    logger.debug(f"Creating subscription for user_id={user_id} with type={subscription_type_id}")

    stmt = insert(Subscription).values(**subscription_data).returning(Subscription)
    result = await db.execute(stmt)
    await db.commit()

    created = result.scalar_one()
    logger.info(f"Subscription created for user_id={user_id}, subscription_id={created.id}")
    return created


# Обновление статуса подписки
async def update_subscription_statuses():
    db = db_session_ctx.get()
    now = datetime.utcnow()

    logger.debug("Deactivating expired subscriptions...")
    stmt = (
        update(Subscription)
        .where(Subscription.end_date < now)
        .where(Subscription.is_active == True)
        .values(is_active=False)
    )
    await db.execute(stmt)
    await db.commit()

    logger.info("Expired subscriptions deactivated")

# Достаем все виды подписок
async def get_all_subscription_types():
    db = db_session_ctx.get()
    logger.debug("Fetching all subscription types")

    result = await db.execute(select(SubscriptionType))
    types = result.scalars().all()

    logger.info(f"Found {len(types)} subscription types")
    return types

# Активация (оплата) подписки
async def activate_user_subscription(user_id: int) -> Subscription | None:
    db = db_session_ctx.get()
    logger.debug(f"Activating subscription for user_id={user_id}")

    stmt = (
        update(Subscription)
        .where(Subscription.user_id == user_id, Subscription.is_active == False)
        .values(is_active=True)
        .returning(Subscription)
    )
    result = await db.execute(stmt)
    await db.commit()

    activated = result.scalar_one_or_none()
    if activated:
        logger.info(f"Subscription activated for user_id={user_id}")
    else:
        logger.warning(f"No inactive subscription to activate for user_id={user_id}")

    return activated

# Смена типа подписки
async def update_user_subscription_type(user_id: int, new_type_id: int) -> Subscription | None:
    db = db_session_ctx.get()
    logger.debug(f"Updating subscription type for user_id={user_id} to type_id={new_type_id}")

    stmt = (
        update(Subscription)
        .where(Subscription.user_id == user_id, Subscription.is_active == True)
        .values(subscription_type_id=new_type_id, is_active=False)
        .returning(Subscription)
    )
    result = await db.execute(stmt)
    await db.commit()

    updated = result.scalar_one_or_none()
    if updated:
        logger.info(f"Subscription updated for user_id={user_id} to type_id={new_type_id}")
    else:
        logger.warning(f"No active subscription found to update for user_id={user_id}")

    return updated