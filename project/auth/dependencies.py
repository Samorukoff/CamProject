from dataclasses import dataclass
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from project.auth.models import User
from project.auth.repositories import get_user_by_id
from project.auth.utils.jwt import verify_access_token
from project.employee.repositories import get_membership
from project.core.config.logging.logger import logger

bearer = HTTPBearer(auto_error=True)

# Определение авторизированного пользователя по токену
async def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(bearer)
) -> User:
    raw = token.credentials
    try:
        payload = verify_access_token(raw)  # должен проверить подпись/exp
    except Exception as e:
        logger.warning(f"[auth] token decode error: {e.__class__.__name__}")
        raise HTTPException(status_code=401, detail="Invalid token")

    if not payload or payload.get("type") != "access":
        logger.warning("[auth] invalid token payload or wrong type")
        raise HTTPException(status_code=401, detail="Invalid token")

    sub = payload.get("sub")
    if sub is None:
        logger.warning("[auth] missing sub")
        raise HTTPException(status_code=401, detail="Invalid token subject")

    try:
        user_id = int(sub)
    except (TypeError, ValueError):
        logger.warning(f"[auth] bad sub value: {sub!r}")
        raise HTTPException(status_code=401, detail="Invalid token subject")

    user = await get_user_by_id(user_id)
    if not user:
        logger.warning(f"[auth] user not found: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")

    logger.debug(f"[auth] OK user_id={user.id}")
    return user

# Определение админки
@dataclass
class AdminContext:
    user: User
    company_id: int

async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
) -> AdminContext:
    token = credentials.credentials
    payload = verify_access_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token")

    cid = payload.get("cid")
    sub = payload.get("sub")
    if cid is None:
        raise HTTPException(status_code=400, detail="No company selected")
    if sub is None:
        raise HTTPException(status_code=401, detail="Invalid token subject")

    try:
        company_id = int(cid)
        user_id = int(sub)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid token claims")

    user = await get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    membership = await get_membership(company_id=company_id, user_id=user_id)
    if not membership or membership.role != "admin":
        logger.warning(f"[get_current_admin_ctx] DENY user_id={user_id} company_id={company_id} role={getattr(membership, 'role', None)}")
        raise HTTPException(status_code=403, detail="Admin rights required")

    logger.info(f"[get_current_admin_ctx] OK user_id={user_id} company_id={company_id}")
    return AdminContext(user=user, company_id=company_id)