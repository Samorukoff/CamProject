from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import StreamingResponse
from io import StringIO
import csv

from project.auth.dependencies import get_current_user
from project.auth.models import User
from project.database import get_db
from project.analysis.schemas import AnalysisRow, AnalysisSummary, PointOut
from project.analysis.services import get_analysis_rows, get_summary, fetch_all_points

router = APIRouter()

# Все точки что есть в сервисе от всех компаний
@router.get("/analysis/points", response_model=list[PointOut],
            summary="Все точки всех компаний",
            description="Общая информация по всем доступным точкам сервиса: названия, адреса, компании")
async def get_points(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await fetch_all_points(db)

# Сводная информация по точкам компании
@router.get("/analysis", response_model=AnalysisSummary,
            summary="Сводка по подписке и доступу",
            description="Тип подписки, стоимость, срок, число доступных камер.")
async def analysis_summary(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    summary = await get_summary(user.id, db)
    if not summary:
        raise HTTPException(status_code=403, detail="No active subscription")
    return summary

# Таблица с подробной информацией
@router.get("/analysis/table", response_model=list[AnalysisRow],
            summary="Сводная таблица",
            description="Аналитическая информация по всем доступным по подписке точкам")
async def analysis_table(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await get_analysis_rows(user.id, db)

# Выгрузка таблицы
@router.get("/analysis/table/export",
            summary="Выгрузка сводной таблицы",
            description="Аналитическая информация по всем доступным по подписке точкам в CSV формате")
async def export_analysis_table(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    rows = await get_analysis_rows(user.id, db)

    stream = StringIO()
    writer = csv.writer(stream)
    writer.writerow(["point_id", "point_name", "camera_name", "traffic", "useful_traffic", "recommendations", "period"])
    for r in rows:
        writer.writerow([r.point_id, r.point_name, r.camera_name, r.traffic, r.useful_traffic, r.recommendations, r.period])

    stream.seek(0)
    return StreamingResponse(
        stream,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=analysis.csv"}
    )