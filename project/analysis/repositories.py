from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
from project.analysis.models import AnalysisData
from project.subscribe.models import Subscription, SubscriptionType
from project.analysis.models import Point
from project.context import db_session_ctx

# Выгрузка из БД всех точек всех компаний
async def get_all_points():
    db = db_session_ctx.get()
    result = await db.execute(select(Point))
    return result.scalars().all()

async def get_analysis_data_for_company(company_id: int):
    db = db_session_ctx.get()
    stmt = (
        select(AnalysisData)
        .join(AnalysisData.point)
        .options(joinedload(AnalysisData.point))
        .where(Point.company == company_id)
    )
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_analysis_summary(company_id: int):
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
    return result.first()