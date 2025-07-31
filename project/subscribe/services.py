from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from project.subscribe.repositories import (
    get_user_subscription,
    create_subscription_for_user,
    update_user_subscription_type
)

# Находим/создаем подписку
async def get_or_create_subscription(user_id: int, db: AsyncSession, subscription_type_id: int):

    # Пробуем найти активную подписку
    existing = await get_user_subscription(db, user_id)

    if existing:
        return existing

    # Подписки нет — создаём новую
    now = datetime.utcnow()
    return await create_subscription_for_user(
        db=db,
        user_id=user_id,
        subscription_type_id=subscription_type_id
    )

# Заглушка оплаты (эмуляция)
async def simulate_payment(user_id: int, db: AsyncSession) -> bool:
    # Тут может быть логика взаимодействия с платежной системой
    # Пока всегда возвращаем True — будто платёж успешен
    return True

# Обновление типа подписки (смена тарифа)
async def change_subscription_type(user_id: int, new_type_id: int, db: AsyncSession):
    subscription = await get_user_subscription(db, user_id)

    if not subscription:
        raise ValueError("No active subscription found")

    return await update_user_subscription_type(
        user_id=user_id,
        new_type_id=new_type_id,
        db=db,
    )