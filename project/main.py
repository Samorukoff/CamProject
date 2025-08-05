from fastapi import FastAPI, Depends
from project.core.utils.startup import run_startup_tasks
from project.core.router import api_router
from project.core.utils.docs_config import custom_openapi
from project.core.config.database.context import set_session_context

app = FastAPI(dependencies=[Depends(set_session_context)])

# Подключение роутеров
app.include_router(api_router)

# Кастомизация Swagger
app.openapi = lambda: custom_openapi(app)

# Запуск фоновых задач
run_startup_tasks(app)