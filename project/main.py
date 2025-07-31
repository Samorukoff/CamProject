from fastapi import FastAPI
from contextlib import asynccontextmanager
from project.dashboard.routers import router as dashboard_router
from project.auth.routers import router as auth_router
from project.subscribe.routers import router as subscribe_router
from project.analysis.routers import router as analysis_router
from project.database import Base, engine
from fastapi.openapi.utils import get_openapi
import logging

from project.subscribe.models import SubscriptionType
from project.analysis.models import Point
from project.company.models import Company 

from project.utils.scheduler import start_subscription_scheduler

logging.basicConfig(level=logging.DEBUG)

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # старт шедулера
    start_subscription_scheduler()

    yield

app = FastAPI(lifespan=lifespan)

# Роутеры по своим префиксам
app.include_router(auth_router, tags=["auth"])
app.include_router(dashboard_router, tags=["dashboard"])
app.include_router(subscribe_router, tags=["subscribe"])
app.include_router(analysis_router, tags=["analysis"])

# Кастомизация Swagger для поддержки OAuth2
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="CamProject API",
        version="1.0.0",
        description="API for CamProject",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": "/auth/login",
                    "scopes": {}
                }
            }
        }
    }
    openapi_schema["security"] = [{"OAuth2PasswordBearer": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi