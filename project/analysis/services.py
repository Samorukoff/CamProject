from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from project.analysis.repositories import (
    get_all_points,
    get_analysis_data_for_company,
    get_analysis_summary
)
from project.analysis.schemas import AnalysisRow, AnalysisSummary
from project.subscribe.repositories import get_user_subscription
from datetime import datetime

# Запускает выгрузку всех точек всех компаний
async def fetch_all_points():
    return await get_all_points()

async def get_analysis_rows(user_id: int):
    subscription = await get_user_subscription(user_id)
    if not subscription or not subscription.subscription_type:
        return []

    company_id = subscription.subscription_type.company
    data = await get_analysis_data_for_company(company_id)

    rows = []
    for item in data:
        rows.append(AnalysisRow(
            point_id=item.point_id,
            point_name=item.point.name,
            camera_name=item.camera,
            traffic=item.traffic,
            useful_traffic=item.useful_traffic,
            recommendations=item.recommendations,
            period=item.period
        ))

    return rows

async def get_summary(user_id: int):
    subscription = await get_user_subscription(user_id)
    if not subscription or not subscription.subscription_type:
        raise HTTPException(status_code=403, detail="No active subscription")

    company_id = subscription.subscription_type.company
    total_points, total_cameras, last_updated = await get_analysis_summary(company_id)

    return AnalysisSummary(
        subscription=subscription.subscription_type.name,
        price=subscription.subscription_type.price,
        remaining_days=(subscription.end_date - datetime.utcnow()).days,
        total_cameras=total_cameras or 0,
        last_updated=last_updated or datetime.utcnow()
    )