from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
from project.analysis.models import AnalysisData
from project.analysis.models import Point
from project.core.config.database.context import db_session_ctx

from project.core.config.logging.logger import logger

# Выгрузка из БД всех точек всех компаний
async def get_all_points():
    logger.debug("Fetching all points from DB")
    db = db_session_ctx.get()
    result = await db.execute(select(Point))
    points = result.scalars().all()
    logger.info(f"Fetched {len(points)} points")
    return points

# Выгрузка из БД аналитических данных по точкам для конкретной компании
async def get_analysis_data_for_company(company_id: int):
    logger.debug(f"Fetching analysis data for company_id={company_id}")
    db = db_session_ctx.get()
    stmt = (
        select(AnalysisData)
        .join(AnalysisData.point)
        .options(joinedload(AnalysisData.point))
        .where(Point.company == company_id)
    )
    result = await db.execute(stmt)
    data = result.scalars().all()
    logger.info(f"Fetched {len(data)} analysis records for company_id={company_id}")
    return data

# Выгрузка из БД сводки для конкретной компании
async def get_analysis_summary(company_id: int):
    logger.debug(f"Calculating summary for company_id={company_id}")
    db = db_session_ctx.get()
    stmt = (
        select(
            func.count(func.distinct(AnalysisData.point_id)),
            func.count(func.distinct(AnalysisData.camera)),
            func.max(AnalysisData.period)
        )
        .join(AnalysisData.point)
        .where(Point.company == company_id)
    )
    result = await db.execute(stmt)
    summary = result.first()
    logger.info(f"Summary for company_id={company_id}: {summary}")
    return summary