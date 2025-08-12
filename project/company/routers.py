from fastapi import APIRouter, Depends
from project.auth.models import User
from project.auth.dependencies import get_current_user
from project.core.config.logging.logger import logger
from project.auth.schemas import Token
from project.company.schemas import CompanyCreateIn, CompanyOut, CompanyLoginIn
from project.company.services import (
    create_company,
    list_admin_companies,
    select_company_as_admin,
)

router = APIRouter()


@router.get("/company", response_model=list[CompanyOut], summary="Мои компании (я админ)")
async def my_admin_companies(
    current_user: User = Depends(get_current_user),
):
    logger.info(f"User {current_user.id} requests admin companies")
    return await list_admin_companies(user_id=current_user.id)


@router.post("/company/create", response_model=CompanyOut, summary="Создать компанию")
async def create_company_route(
    payload: CompanyCreateIn,
    current_user: User = Depends(get_current_user),
):
    logger.info(f"User {current_user.id} creates company '{payload.name}'")
    return await create_company(actor_id=current_user.id, data=payload)


@router.post("/company/login", response_model=Token, summary="Выбрать компанию (только админ)")
async def login_company_route(
    payload: CompanyLoginIn,
    current_user: User = Depends(get_current_user),
):
    logger.info(f"User {current_user.id} selects company {payload.company_id}")
    return await select_company_as_admin(actor_id=current_user.id, company_id=payload.company_id)
