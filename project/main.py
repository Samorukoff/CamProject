from fastapi import FastAPI, Depends
from project.core.config.lifespan import lifespan
from project.core.router import api_router
from project.core.utils.openapi import custom_openapi

from project.subscribe.models import SubscriptionType
from project.analysis.models import Point
from project.company.models import Company
from project.core.config.database.context import set_session_context

app = FastAPI(lifespan=lifespan, dependencies=[Depends(set_session_context)])

app.include_router(api_router)

app.openapi = lambda: custom_openapi(app)