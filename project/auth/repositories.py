from sqlalchemy.ext.asyncio import AsyncSession
from project.auth.models import User
from sqlalchemy import select
from project.context import db_session_ctx

# Добавление пользователя в БД
async def register_user_in_db(user: User):
    db = db_session_ctx.get()
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

# Поиск пользователя по имени в БД
async def get_user_by_name(full_name: str) -> User | None:
    db = db_session_ctx.get()
    result = await db.execute(select(User).where(User.full_name == full_name))
    return result.scalar_one_or_none()