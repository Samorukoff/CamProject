from io import BytesIO
from openpyxl import Workbook

from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from project.analysis.repositories import (
    get_all_points,
    get_analysis_data_for_company,
    get_analysis_summary
)
from project.analysis.schemas import AnalysisRow, AnalysisSummary
from project.subscribe.repositories import get_user_subscription
from datetime import datetime

from project.core.config.logging.logger import logger

# --- helpers / constants ---

_HEADERS = [
    "point_id",
    "point_name",
    "camera_name",
    "traffic",
    "useful_traffic",
    "recommendations",
    "period",
]

async def _fetch_active_subscription(user_id: int):
    """Единая точка получения подписки (без выброса HTTP ошибок)."""
    logger.debug(f"[subscription] fetch for user_id={user_id}")
    sub = await get_user_subscription(user_id)
    return sub if (sub and sub.subscription_type) else None

def _format_period(period) -> str:
    fmt = getattr(period, "strftime", None)
    return fmt("%Y-%m-%d") if callable(fmt) else str(period)

def _item_to_row(item) -> AnalysisRow:
    return AnalysisRow(
        point_id=item.point_id,
        point_name=item.point.name,
        camera_name=item.camera,
        traffic=item.traffic,
        useful_traffic=item.useful_traffic,
        recommendations=item.recommendations,
        period=item.period,
    )

def _rows_to_workbook(rows: list[AnalysisRow], sheet_title: str = "Аналитика") -> Workbook:
    wb = Workbook()
    sh = wb.active
    sh.title = sheet_title
    sh.append(_HEADERS)
    for r in rows:
        sh.append([
            r.point_id,
            r.point_name,
            r.camera_name,
            r.traffic,
            r.useful_traffic,
            r.recommendations,
            _format_period(r.period),
        ])
    return wb

def _workbook_to_stream(wb: Workbook, filename: str) -> StreamingResponse:
    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )

# Запускает выгрузку всех точек всех компаний
async def fetch_all_points(company_id: int):
    logger.debug("Fetching all points from repository")
    points = await get_all_points(company_id)
    logger.info(f"Fetched {len(points)} points from DB for company ID: {company_id}")
    return points

# Выгрузка аналитических данных
async def get_analysis_rows(user_id: int, company_id: int) -> list[AnalysisRow]:
    logger.debug(f"Getting analysis rows for user_id={user_id}")

    subscription = await _fetch_active_subscription(user_id)
    if not subscription:
        logger.warning(f"No active subscription for user_id={user_id}")
        raise HTTPException(status_code=404, detail="Active subscription not found")

    data = await get_analysis_data_for_company(company_id) or []
    logger.info(f"Fetched {len(data)} analysis records for company_id={company_id}")

    rows = [_item_to_row(item) for item in data]
    logger.debug(f"Built {len(rows)} AnalysisRow objects for export")
    return rows

# Построение таблицы Excel
async def construct_table(user_id: int, company_id: int):
    logger.info(f"Starting Excel export for user_id={user_id}")

    rows = await get_analysis_rows(user_id, company_id)
    if not rows:
        logger.warning(f"No data to export for user_id={user_id}")

    wb = _rows_to_workbook(rows, sheet_title="Аналитика")
    logger.debug(f"Excel file built with {len(rows)} rows")

    logger.info(f"Excel export completed for user_id={user_id}")
    return _workbook_to_stream(wb, filename="analysis.xlsx")

# Сводная информация по подписке и доступным точкам
async def get_summary(user_id: int, company_id: int):
    logger.debug(f"Getting summary for user_id={user_id}")

    subscription = await _fetch_active_subscription(user_id)
    if not subscription:
        logger.warning(f"No active subscription found for user_id={user_id}")
        raise HTTPException(status_code=403, detail="No active subscription")

    total_points, total_cameras, last_updated = await get_analysis_summary(company_id)
    logger.info(f"Summary for user_id={user_id}: {total_points} points, {total_cameras} cameras")

    return AnalysisSummary(
        subscription=subscription.subscription_type.name,
        price=subscription.subscription_type.price,
        remaining_days=(subscription.end_date - datetime.utcnow()).days,
        total_cameras=total_cameras or 0,
        last_updated=last_updated or datetime.utcnow(),
    )