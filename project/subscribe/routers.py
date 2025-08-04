from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from project.auth.dependencies import get_current_user
from project.database import get_db
from project.subscribe.schemas import (
    SubscriptionRead,
    SubscriptionUserSelect,
    SubscriptionTypeOut,
)
from project.subscribe.repositories import (
    get_all_subscription_types,
    activate_user_subscription,
)
from project.subscribe.services import (
    get_or_create_subscription,
    change_subscription_type,
    simulate_payment,
)
from project.auth.models import User

router = APIRouter()


@router.post("/subscribe", response_model=SubscriptionRead,
            summary="Подписка",
            description="Выбор подписки по определенному типу")
async def subscribe_user(
    payload: SubscriptionUserSelect,
    current_user: User = Depends(get_current_user)
):
    subscription = await get_or_create_subscription(
        user_id=current_user.id,
        subscription_type_id=payload.subscription_type_id
    )
    return subscription


@router.get("/subscribe/types", response_model=list[SubscriptionTypeOut],
            summary="Виды подписок",
            description="Перечень всех доступных подписок. ID, компании, цена")
async def list_subscription_types(
    user: User = Depends(get_current_user)
):
    types = await get_all_subscription_types()
    return types


@router.post("/subscribe/pay",
            summary="Оплата",
            description="Активация статуса подписки с помощью симуляции оплаты (заглушка)")
async def pay_subscription(
    current_user: User = Depends(get_current_user)
):
    # Заглушка оплаты
    payment_success = await simulate_payment(current_user.id)
    if not payment_success:
        raise HTTPException(status_code=402, detail="Payment failed")

    # Активация подписки
    activated = await activate_user_subscription(current_user.id)
    if not activated:
        raise HTTPException(status_code=404, detail="Subscription not found")

    return {"action": "redirect", "to": "/"}


@router.put("/subscribe/change",
            summary="Смена тарифа",
            description="Замена текущего ID подписки на другой, сброс статуса, снова требуется оплата")
async def change_subscription(
    payload: SubscriptionUserSelect,
    current_user: User = Depends(get_current_user),
):
    changed = await change_subscription_type(
        user_id=current_user.id,
        new_type_id=payload.subscription_type_id
    )
    if not changed:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return {"action": "redirect", "to": "/"}


