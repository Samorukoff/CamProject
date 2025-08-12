from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from project.auth.dependencies import get_current_admin
from project.auth.models import User
from project.analysis.schemas import AnalysisRow, AnalysisSummary, PointOut
from project.analysis.services import get_analysis_rows, construct_table, get_summary, fetch_all_points

from project.core.config.logging.logger import logger

router = APIRouter()

# Все точки компании
@router.get("/analysis/points", response_model=list[PointOut],
            summary="Все точки вашей компании",
            description="Общая информация по всем доступным точкам сервиса: названия, адреса, компании (доступно без подписки)")
async def get_points(
    user: User = Depends(get_current_admin)
):
    logger.info(f"User {user.id} requested all service points")
    return await fetch_all_points(user.company_id)

# Сводная информация по точкам компании
@router.get("/analysis", response_model=AnalysisSummary,
            summary="Сводка по подписке и доступу",
            description="Тип подписки, стоимость, срок, число доступных камер.")
async def analysis_summary(
    user: User = Depends(get_current_admin)
):
    logger.info(f"User {user.id} requested subscription summary")
    return await get_summary(user.id, user.company_id)

# Таблица с подробной информацией
@router.get("/analysis/table", response_model=list[AnalysisRow],
            summary="Сводная таблица",
            description="Аналитическая информация по всем доступным по подписке точкам")
async def analysis_table(
    user: User = Depends(get_current_admin)
):
    logger.info(f"User {user.id} requested analysis table")
    return await get_analysis_rows(user.id, user.company_id)

# Выгрузка таблицы Excel
@router.get("/analysis/table/export",
            response_class=StreamingResponse,
            summary="Выгрузка сводной таблицы",
            description="Аналитическая информация по всем доступным по подписке точкам в xlsx формате")
async def export_analysis_table(
    user: User = Depends(get_current_admin)
):
    logger.info(f"User {user.id} requested Excel export of analysis table")
    return await construct_table(user.id, user.company_id)