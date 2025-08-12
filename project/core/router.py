from fastapi import APIRouter
from project.auth.routers import router as auth_router
from project.analysis.routers import router as analysis_router
from project.subscribe.routers import router as subscribe_router
from project.dashboard.routers import router as dashboard_router
from project.company.routers import router as company_router
from project.employee.routers import router as employee_router

api_router = APIRouter()

# Подключаем всё централизованно
api_router.include_router(auth_router, tags=["auth"])
api_router.include_router(analysis_router, tags=["analysis"])
api_router.include_router(subscribe_router, tags=["subscribe"])
api_router.include_router(dashboard_router, tags=["dashboard"])
api_router.include_router(company_router, tags=["company"])
api_router.include_router(employee_router, tags=["employee"])