from fastapi import APIRouter, Depends, HTTPException
from project.auth.dependencies import get_current_admin, AdminContext
from project.subscribe.schemas import (
    SubscriptionRead,
    SubscriptionUserSelect,
    SubscriptionTypeOut,
)
from project.subscribe.services import (
    get_or_create_subscription,
    change_subscription_type,
    simulate_payment,
    fetch_subscription_types
)
from project.auth.models import User
from project.core.config.logging.logger import logger

router = APIRouter()


@router.post("/subscribe", response_model=SubscriptionRead,
            summary="Подписка",
            description="Выбор подписки по определенному типу")
async def subscribe_user(
    payload: SubscriptionUserSelect,
    ctx: AdminContext = Depends(get_current_admin),
):
    logger.info(f"User {ctx.user.id} is subscribing to {payload.subscription_type_id}")
    subscription = await get_or_create_subscription(
        user_id=ctx.user.id,
        subscription_type_id=payload.subscription_type_id
    )
    return subscription


@router.get("/subscribe/types", response_model=list[SubscriptionTypeOut],
            summary="Виды подписок",
            description="Перечень всех доступных подписок. ID, компании, цена")
async def list_subscription_types(
    ctx: AdminContext = Depends(get_current_admin),
):
    logger.info(f"User {ctx.user.id} requested list of subscription types")
    types = await fetch_subscription_types()
    return types


@router.post("/subscribe/pay",
            summary="Оплата",
            description="Активация статуса подписки с помощью симуляции оплаты (заглушка)")
async def pay_subscription(
    ctx: AdminContext = Depends(get_current_admin),
):
    # Заглушка оплаты
    logger.info(f"User {ctx.user.id} is attempting to pay")
    result = await simulate_payment(ctx.user.id)

    return result


@router.put("/subscribe/change",
            summary="Смена тарифа",
            description="Замена текущего ID подписки на другой, сброс статуса, снова требуется оплата")
async def change_subscription(
    payload: SubscriptionUserSelect,
    ctx: AdminContext = Depends(get_current_admin),
):
    logger.info(f"User {ctx.user.id} requests change of subscription to {payload.subscription_type_id}")
    changed = await change_subscription_type(
        user_id=ctx.user.id,
        new_type_id=payload.subscription_type_id
    )
    if not changed:
        logger.warning(f"Subscription not found for user {ctx.user.id}")
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    return changed


