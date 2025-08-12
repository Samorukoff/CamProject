from fastapi import HTTPException
from project.company.schemas import CompanyCreateIn, CompanyOut
from project.auth.schemas import Token
from project.company.repositories import (
    create_company_repo,
    list_admin_companies_for_user,
)
from project.employee.repositories import (
    get_membership,
    create_membership,
)
from project.auth.utils.jwt import create_access_token, create_refresh_token
from project.core.config.logging.logger import logger

# Вывод списка компаний, в которых имеется админка
async def list_admin_companies(user_id: int) -> list[CompanyOut]:
    logger.info(f"[list_admin_companies] user_id={user_id}")

    companies = await list_admin_companies_for_user(user_id)

    logger.info(f"[list_admin_companies] found={len(companies)} user_id={user_id}")
    logger.debug(f"[list_admin_companies] company_ids={[c.id for c in companies]}")
    return [CompanyOut(id=company.id, name=company.name) for company in companies]

# Создание новой компании
async def create_company(actor_id: int, data: CompanyCreateIn) -> CompanyOut:
    logger.info(f"[create_company] actor_id={actor_id} name={data.name!r}")

    company = await create_company_repo(name=data.name)

    logger.info(f"[create_company] company_created id={company.id} name={company.name!r}")
    # создатель — админ и владелец
    created_membership = await create_membership(company_id=company.id, user_id=actor_id, role="admin", is_owner=True)
    logger.info(f"[create_company] membership_created id={created_membership.id} company_id={company.id} user_id={actor_id} role=admin owner=True")
    return CompanyOut(id=company.id, name=company.name)

# Выбор компании для входа в админку
async def select_company_as_admin(actor_id: int, company_id: int) -> Token:
    logger.info(f"[select_company_as_admin] actor_id={actor_id} company_id={company_id}")

    actor_membership = await get_membership(company_id=company_id, user_id=actor_id)
    if not (actor_membership and actor_membership.role == "admin"):
        logger.warning(f"[select_company_as_admin] DENY actor_id={actor_id} company_id={company_id} role={getattr(actor_membership, 'role', None)}")
        raise HTTPException(status_code=403, detail="Admin rights required")
    
    logger.info(f"[select_company_as_admin] OK actor_id={actor_id} company_id={company_id} role=admin")

    access = create_access_token({"sub": str(actor_id), "cid": company_id, "type": "access"})
    refresh = create_refresh_token({"sub": str(actor_id), "cid": company_id, "type": "refresh"})

    logger.info(f"[select_company_as_admin] tokens_issued actor_id={actor_id} company_id={company_id}")
    return Token(access_token=access, refresh_token=refresh)
