from fastapi import HTTPException
from typing import Optional
from pydantic import EmailStr
from project.employee.schemas import EmployeeOut, EmployeeLookupOut
from project.employee.repositories import (
    get_membership,
    list_memberships_with_users,
    create_membership,
    delete_membership,
    count_admins,
    set_role_admin,
)
from project.auth.repositories import get_user_by_id, get_user_by_email
from project.core.config.logging.logger import logger

# Вывод сотрудников
def _to_employee_out(membership, user=None) -> EmployeeOut:
    """Собираем DTO. Если user не передан, берём membership.user (для list_*)."""
    u = user or membership.user
    # подробный лог на debug, чтобы не флудить
    logger.debug(f"[_to_employee_out] user_id={u.id} email={u.email} role={membership.role} owner={membership.is_owner}")
    return EmployeeOut(
        user_id=u.id,
        email=u.email,
        full_name=getattr(u, "full_name", None),
        role=membership.role,
        is_owner=membership.is_owner,
    )

# Нормализация адреса почты
def _norm_email(email: str) -> str:
    return email.strip().lower()

# Поиск пользователя по почте
async def find_user_by_email(email: EmailStr) -> Optional[EmployeeLookupOut]:
    e = _norm_email(str(email))
    logger.info(f"[find_user_by_email] lookup={e}")
    user = await get_user_by_email(e)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return EmployeeLookupOut(id=user.id, email=user.email, full_name=getattr(user, "full_name", None))

# Вывод списка работников компании
async def list_employees(actor_id: int, company_id: int) -> list[EmployeeOut]:
    logger.info(f"[list_employees] actor_id={actor_id} company_id={company_id}")

    memberships = await list_memberships_with_users(company_id)  # user уже подгружен

    logger.info(f"[list_employees] members_count={len(memberships)} company_id={company_id}")
    return [_to_employee_out(membership) for membership in memberships]

# Добавление работнкиа в компанию
async def add_employee(actor_id: int, company_id: int, target_user_id: int, role: str, is_owner: bool) -> EmployeeOut:
    logger.info(f"[add_employee] actor_id={actor_id} company_id={company_id} target_user_id={target_user_id} role={role} is_owner={is_owner}")

    user = await get_user_by_id(target_user_id)
    if not user:
        logger.warning(f"[add_employee] target user not found target_user_id={target_user_id}")
        raise HTTPException(status_code=404, detail="Target user not found")

    if await get_membership(company_id, target_user_id):
        logger.warning(f"[add_employee] already a member company_id={company_id} target_user_id={target_user_id}")
        raise HTTPException(status_code=409, detail="Already a member")

    created = await create_membership(company_id, target_user_id, role, is_owner)
    logger.info(f"[add_employee] CREATED membership_id={created.id} company_id={company_id} target_user_id={target_user_id}")
    return _to_employee_out(created, user)

# Удаление работника из компании
async def delete_employee(actor_id: int, company_id: int, target_user_id: int) -> None:
    logger.info(f"[delete_employee] actor_id={actor_id} company_id={company_id} target_user_id={target_user_id}")

    target = await get_membership(company_id, target_user_id)
    if not target:
        logger.info(f"[delete_employee] membership not found company_id={company_id} target_user_id={target_user_id}")
        return
    if target.is_owner:
        logger.warning(f"[delete_employee] cannot remove owner company_id={company_id} target_user_id={target_user_id}")
        raise HTTPException(status_code=403, detail="Cannot remove company owner")
    if target.role == "admin":
        admins = await count_admins(company_id)
        logger.debug(f"[delete_employee] admins_count={admins} company_id={company_id}")
        if admins <= 1:
            logger.warning(f"[delete_employee] cannot remove last admin company_id={company_id} target_user_id={target_user_id}")
            raise HTTPException(status_code=403, detail="Cannot remove the last admin")

    await delete_membership(company_id, target_user_id)
    logger.info(f"[delete_employee] DELETED company_id={company_id} target_user_id={target_user_id}")

# Добавление админки работнику компании
async def make_admin(actor_id: int, company_id: int, target_user_id: int) -> EmployeeOut:
    logger.info(f"[make_admin] actor_id={actor_id} company_id={company_id} target_user_id={target_user_id}")
    
    target = await get_membership(company_id, target_user_id)
    if not target:
        logger.warning(f"[make_admin] target not in company company_id={company_id} target_user_id={target_user_id}")
        raise HTTPException(status_code=404, detail="Target user not in company")

    updated = await set_role_admin(company_id, target_user_id)
    logger.info(f"[make_admin] role updated to admin membership_id={updated.id} company_id={company_id} target_user_id={target_user_id}")
    user = await get_user_by_id(target_user_id)
    return _to_employee_out(updated, user)