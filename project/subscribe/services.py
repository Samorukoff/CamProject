from fastapi import HTTPException
from datetime import datetime
from project.subscribe.repositories import (
    get_user_subscription,
    create_subscription_for_user,
    update_user_subscription_type,
    activate_user_subscription,
    get_all_subscription_types
)

from project.core.config.logging.logger import logger

# Вызываем запрос на выдачу всех типов подписок
async def fetch_subscription_types():
    logger.debug("Fetching all subscription types")
    types = await get_all_subscription_types()
    logger.info(f"Found {len(types)} subscription types")
    return types

# Находим/создаем подписку
async def get_or_create_subscription(user_id: int, subscription_type_id: int):
    logger.debug(f"Checking for subscription for user {user_id}")

    # Пробуем найти активную подписку
    existing = await get_user_subscription(user_id)

    if existing:
        logger.info(f"Subscription already exists for user {user_id}")
        return existing

    # Подписки нет — создаём новую
    logger.info(f"Creating new subscription for user {user_id} with type {subscription_type_id}")
    return await create_subscription_for_user(
        user_id=user_id,
        subscription_type_id=subscription_type_id
    )

# Заглушка оплаты (эмуляция)
async def simulate_payment(user_id: int) -> bool:
    # Тут может быть логика взаимодействия с платежной системой
    # Пока всегда возвращаем True — будто платёж успешен
    logger.info(f"Simulating payment for user {user_id}")

    # Эмуляция успеха
    payment_success = True
    if not payment_success:
        logger.warning(f"Payment failed for user {user_id}")
        raise HTTPException(status_code=402, detail="Payment failed")

    # Проверяем подписку
    existing = await get_user_subscription(user_id)
    if existing and existing.is_active:
        logger.info(f"User {user_id} already has active subscription (id={existing.id})")
        return {
            "status": "already_active",
            "detail": "Subscription is already active.",
            "subscription_id": existing.id
        }

    activated = await activate_user_subscription(user_id)

    if activated:
        logger.info(f"Subscription activated for user {user_id}")
        return {
            "status": "activated",
            "detail": "Subscription successfully activated.",
            "subscription_id": activated.id
        }

    logger.warning(f"No subscription found to activate for user {user_id}")
    return {
        "status": "not_found",
        "detail": "No inactive subscription found to activate."
    }

# Обновление типа подписки (смена тарифа)
async def change_subscription_type(user_id: int, new_type_id: int):
    logger.info(f"Changing subscription for user {user_id} to type {new_type_id}")

    subscription = await get_user_subscription(user_id)

    if not subscription:
        logger.warning(f"No active subscription found for user {user_id}")
        raise HTTPException(status_code=404, detail="Active subscription not found")

    updated = await update_user_subscription_type(user_id, new_type_id)
    logger.info(f"Subscription updated for user {user_id}. New type: {new_type_id}")
    return updated
