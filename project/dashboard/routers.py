from fastapi import APIRouter, Depends

from project.auth.dependencies import get_current_admin
from project.auth.models import User
from project.dashboard.services import determine_dashboard_redirect

from project.core.config.logging.logger import logger

router = APIRouter()


@router.get("/",
            summary="Основной дашборд",
            description="Отображение текущей подписки пользователя и статуса доступа")
async def dashboard_entry(
    user: User = Depends(get_current_admin)
):
    logger.info(f"Dashboard accessed by user_id={user.id}")
    redirect = await determine_dashboard_redirect(user.id)
    return redirect


@router.get("/info", summary="Информация о главной странице")
async def dashboard_info():
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
