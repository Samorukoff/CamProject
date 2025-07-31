from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from project.dashboard.dependencies import get_db
from project.auth.dependencies import get_current_user
from project.auth.models import User

from project.subscribe.repositories import get_user_subscription

router = APIRouter()

@router.get("/",
            summary="Основной дашборд",
            description="Отображение текущей подписки пользователя и статуса доступа")
async def dashboard_entry(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    subscription = await get_user_subscription(db, user.id)
    if not subscription or not subscription.is_active:
        return {"action": "redirect", "to": "/subscribe"}

    return {"action": "redirect", "to": "/analysis"}

@router.get("/info", summary="Информация о главной странице")
async def dashboard_info(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):

    return {
        "title": "Аналитика по камерам и точкам продаж",
        "description": "Подключите подписку, чтобы начать получать аналитику по трафику, полезной проходимости и рекомендациям для улучшения.",
        "features": [
            "Мониторинг посещаемости",
            "Оценка полезной проходимости",
            "Рекомендации по размещению товаров",
            "Экспорт аналитических данных"
        ]
    }
