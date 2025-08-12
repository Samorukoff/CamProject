from fastapi.openapi.utils import get_openapi
from fastapi import FastAPI

def custom_openapi(app: FastAPI):
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title="CamProject API",
        version="1.0.0",
        description="API for CamProject",
        routes=app.routes,
    )

    comps = schema.setdefault("components", {}).setdefault("securitySchemes", {})
    # убираем кастомную схему, если где-то осталась
    comps.pop("BearerAuth", None)

    # глобально требуем именно HTTPBearer (который FastAPI добавил из зависимости)
    schema["security"] = [{"HTTPBearer": []}]

    # снять авторизацию с публичных ручек
    for p in ("/auth/login", "/auth/register", "/auth/refresh", "/info"):
        if p in schema.get("paths", {}):
            for m in schema["paths"][p].values():
                if isinstance(m, dict):
                    m["security"] = []

    app.openapi_schema = schema
    return schema