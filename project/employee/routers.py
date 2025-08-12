from fastapi import APIRouter, Depends
from pydantic import EmailStr
from project.auth.dependencies import get_current_admin, AdminContext
from project.core.config.logging.logger import logger
from project.employee.schemas import EmployeeOut, EmployeeAddIn, EmployeeDeleteIn, EmployeeLookupOut
from project.employee.services import (
    list_employees,
    add_employee,
    delete_employee,
    make_admin,
    find_user_by_email
)

router = APIRouter()


@router.get("/employee", response_model=list[EmployeeOut], summary="Список сотрудников")
async def list_employees_route(
    ctx: AdminContext = Depends(get_current_admin),
):
    logger.info(f"User {ctx.user.id} lists employees of company {ctx.company_id}")
    return await list_employees(actor_id=ctx.user.id, company_id=ctx.company_id)


@router.get("/employee/search", response_model=EmployeeLookupOut, summary="Найти пользователя по e-mail (админ)")
async def find_user(
    email: EmailStr,
    ctx: AdminContext = Depends(get_current_admin),
):
    # ctx нужен лишь для авторизации: админ выбранной компании
    logger.info(f"[users.find] admin={ctx.user.id} company={ctx.company_id} email={email}")
    found = await find_user_by_email(email)
    return found


@router.post("/employee/add", response_model=EmployeeOut, summary="Добавить сотрудника")
async def add_employee_route(
    payload: EmployeeAddIn,
    ctx: AdminContext = Depends(get_current_admin),
):
    logger.info(f"User {ctx.user.id} adds user {payload.user_id} to company {ctx.company_id} as {payload.role}")
    return await add_employee(
        actor_id=ctx.user.id,
        company_id=ctx.company_id,
        target_user_id=payload.user_id,
        role='employee',
        is_owner=False,
    )


@router.delete("/employee/delete", summary="Удалить сотрудника", status_code=204)
async def delete_employee_route(
    payload: EmployeeDeleteIn,
    ctx: AdminContext = Depends(get_current_admin)
):
    logger.info(f"User {ctx.user.id} deletes user {payload.user_id} from company {ctx.company_id}")
    await delete_employee(actor_id=ctx.user.id, company_id=ctx.company_id, target_user_id=payload.user_id)
    return


@router.post("/employee/add/admin", response_model=EmployeeOut, summary="Назначить администратора")
async def make_admin_route(
    payload: EmployeeDeleteIn,   # только user_id
    ctx: AdminContext = Depends(get_current_admin)
):
    logger.info(f"User {ctx.user.id} makes admin {payload.user_id} in company {ctx.company_id}")
    return await make_admin(actor_id=ctx.user.id, company_id=ctx.company_id, target_user_id=payload.user_id)