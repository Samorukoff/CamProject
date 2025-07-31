from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, update, insert
from project.subscribe.models import Subscription, SubscriptionType
from datetime import datetime, timedelta

# Поиск подписки пользователя в БД
async def get_user_subscription(db: AsyncSession, user_id: int) -> Subscription | None:
    stmt = (
        select(Subscription).where(
        Subscription.user_id == user_id,
        Subscription.is_active == True)
        .options(selectinload(Subscription.subscription_type))
    )
    result = await db.execute(stmt)
    return result.scalars().first()

# Создание подписки пользователя в БД
async def create_subscription_for_user(db, user_id: int, subscription_type_id: int):
    now = datetime.utcnow()
    subscription_data = {
        "user_id": user_id,
        "subscription_type_id": subscription_type_id,
        "start_date": now,
        "end_date": now + timedelta(days=30),
        "is_active": False,
    }
    stmt = insert(Subscription).values(**subscription_data).returning(Subscription)
    result = await db.execute(stmt)
    await db.commit()
    return result.scalar_one()

# Обновление статуса подписки
async def update_subscription_statuses(db: AsyncSession):
    now = datetime.utcnow()
    stmt = (
        update(Subscription)
        .where(Subscription.end_date < now)
        .where(Subscription.is_active == True)
        .values(is_active=False)
    )
    await db.execute(stmt)
    await db.commit()

# Достаем все виды подписок
async def get_all_subscription_types(db: AsyncSession):
    result = await db.execute(select(SubscriptionType))
    return result.scalars().all()

# Активация (оплата) подписки
async def activate_user_subscription(user_id: int, db: AsyncSession) -> Subscription | None:
    stmt = (
        update(Subscription)
        .where(Subscription.user_id == user_id, Subscription.is_active == False)
        .values(is_active=True)
        .returning(Subscription)
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.scalar_one_or_none()

# Смена типа подписки
async def update_user_subscription_type(user_id: int, new_type_id: int, db: AsyncSession) -> Subscription | None:
    stmt = (
        update(Subscription)
        .where(Subscription.user_id == user_id, Subscription.is_active == True)
        .values(subscription_type_id=new_type_id, is_active=False)
        .returning(Subscription)
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.scalar_one_or_none()