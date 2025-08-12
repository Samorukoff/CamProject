from project.auth.models import User
from project.company.models import Company
from sqlalchemy import select
from project.core.config.database.context import db_session_ctx

from project.core.config.logging.logger import logger

# Добавление пользователя в БД
async def register_user_in_db(user: User):
    logger.debug(f"Registering new user in DB: {user.full_name}")
    db = db_session_ctx.get()
    db.add(user)
    await db.commit()
    await db.refresh(user)
    logger.info(f"User {user.id} successfully registered")
    return user

# Поиск пользователя по почте в БД
async def get_user_by_email(email: str) -> User | None:
    logger.debug(f"Looking up user by email: {email}")
    db = db_session_ctx.get()
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if user:
        logger.info(f"Found user {user.id} for name: {email}")
    else:
        logger.warning(f"No user found with name: {email}")

    return user

# Поиск пользователя по ID в БД
async def get_user_by_id(id: int) -> User | None:
    logger.debug(f"Looking up user by id: {id}")
    db = db_session_ctx.get()
    result = await db.execute(select(User).where(User.id == id))
    user = result.scalar_one_or_none()

    if user:
        logger.info(f"Found user {user.id} for name: {id}")
    else:
        logger.warning(f"No user found with name: {id}")

    return user

# Поиск компании по названию в БД
async def get_company_by_name(name: str) -> Company | None:
    db = db_session_ctx.get()
    result = await db.execute(select(Company).where(Company.name == name))
    return result.scalar_one_or_none()

# Создание новой компании в БД
async def create_company(name: str) -> Company:
    db = db_session_ctx.get()
    company = Company(name=name)
    db.add(company)
    await db.commit()
    await db.refresh(company)
    logger.info(f"Company {company.id} created")
    return company