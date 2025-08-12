from sqlalchemy import select, insert
from project.core.config.database.context import db_session_ctx
from project.company.models import Company
from project.employee.models import CompanyMembership
from project.core.config.logging.logger import logger

# Добавление компании в БД
async def create_company_repo(name: str) -> Company:
    logger.debug(f"[create_company_repo] name={name!r}")
    db = db_session_ctx.get()
    res = await db.execute(
        insert(Company).values(name=name).returning(Company)
    )
    await db.commit()
    company = res.scalar_one()
    logger.info(f"[create_company_repo] CREATED company_id={company.id} name={company.name!r}")
    return company

# Вывод компаний с админкой для пользователя
async def list_admin_companies_for_user(user_id: int) -> list[Company]:
    logger.debug(f"[list_admin_companies_for_user] user_id={user_id}")
    db = db_session_ctx.get()
    # компании, где user — admin
    stmt = (
        select(Company)
        .join(CompanyMembership, CompanyMembership.company_id == Company.id)
        .where(
            CompanyMembership.user_id == user_id,
            CompanyMembership.role == "admin",
        )
        .order_by(Company.id)
    )
    res = await db.execute(stmt)
    companies = list(res.scalars())
    logger.info(f"[list_admin_companies_for_user] found={len(companies)} user_id={user_id}")
    logger.debug(f"[list_admin_companies_for_user] company_ids={[c.id for c in companies]}")
    return companies