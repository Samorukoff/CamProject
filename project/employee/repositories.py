from sqlalchemy import select, insert, delete, update, func
from sqlalchemy.orm import selectinload
from project.core.config.database.context import db_session_ctx
from project.employee.models import CompanyMembership
from project.core.config.logging.logger import logger

# Поиск в БД записи с членством конкретного пользователя в компании
async def get_membership(company_id: int, user_id: int) -> CompanyMembership | None:
    logger.debug(f"[get_membership] company_id={company_id}, user_id={user_id}")
    db = db_session_ctx.get()
    res = await db.execute(
        select(CompanyMembership).where(
            CompanyMembership.company_id == company_id,
            CompanyMembership.user_id == user_id,
        )
    )
    membership = res.scalar_one_or_none()
    if membership:
        logger.info(f"[get_membership] FOUND membership_id={membership.id} (company_id={company_id}, user_id={user_id})")
    else:
        logger.info(f"[get_membership] NOT FOUND (company_id={company_id}, user_id={user_id})")
    return membership

# Выдача списка всех членов компании из БД
async def list_memberships_with_users(company_id: int) -> list[CompanyMembership]:
    logger.debug(f"[list_memberships_with_users] company_id={company_id}")
    db = db_session_ctx.get()
    res = await db.execute(
        select(CompanyMembership)
        .options(selectinload(CompanyMembership.user))
        .where(CompanyMembership.company_id == company_id)
        .order_by(CompanyMembership.id)
    )
    memberships = list(res.scalars())
    logger.info(f"[list_memberships_with_users] count={len(memberships)} (company_id={company_id})")
    return memberships

# Добавление пользователя в компанию
async def create_membership(company_id: int, user_id: int, role: str, is_owner: bool) -> CompanyMembership:
    logger.debug(f"[create_membership] company_id={company_id}, user_id={user_id}, role={role}, is_owner={is_owner}")
    db = db_session_ctx.get()
    res = await db.execute(
        insert(CompanyMembership)
        .values(company_id=company_id, user_id=user_id, role=role, is_owner=is_owner)
        .returning(CompanyMembership)
    )
    await db.commit()
    membership = res.scalar_one()
    logger.info(f"[create_membership] CREATED membership_id={membership.id} company={company_id} user={user_id} role={role} owner={is_owner}")
    return membership

# Удаление пользователя из компании
async def delete_membership(company_id: int, user_id: int) -> None:
    logger.debug(f"[delete_membership] company_id={company_id}, user_id={user_id}")
    db = db_session_ctx.get()
    await db.execute(
        delete(CompanyMembership).where(
            CompanyMembership.company_id == company_id,
            CompanyMembership.user_id == user_id,
        )
    )
    await db.commit()
    logger.info(f"[delete_membership] DELETED (company_id={company_id}, user_id={user_id})")

# Подсчет числа администраторов (на всякий случай чтобы их не было меньше 1)
async def count_admins(company_id: int) -> int:
    logger.debug(f"[count_admins] company_id={company_id}")
    db = db_session_ctx.get()
    res = await db.execute(
        select(func.count()).select_from(CompanyMembership).where(
            CompanyMembership.company_id == company_id,
            CompanyMembership.role == "admin",
        )
    )
    count = int(res.scalar_one())
    logger.info(f"[count_admins] admins={count} (company_id={company_id})")
    return count

# Выдача админки
async def set_role_admin(company_id: int, user_id: int) -> CompanyMembership:
    logger.debug(f"[set_role_admin] company_id={company_id}, user_id={user_id}")
    db = db_session_ctx.get()
    res = await db.execute(
        update(CompanyMembership)
        .where(
            CompanyMembership.company_id == company_id,
            CompanyMembership.user_id == user_id,
        )
        .values(role="admin")
        .returning(CompanyMembership)
    )
    await db.commit()
    logger.info(f"[set_role_admin] role set to 'admin' (company_id={company_id}, user_id={user_id})")
    return res.scalar_one()