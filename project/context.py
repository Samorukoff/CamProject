from contextvars import ContextVar
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from project.database import get_db  # твой обычный get_db

# Контекстная переменная
db_session_ctx: ContextVar[AsyncSession] = ContextVar("db_session_ctx")

# Dependency, который сохраняет сессию в контекст на каждый запрос
async def set_session_context(db: AsyncSession = Depends(get_db)):
    db_session_ctx.set(db)