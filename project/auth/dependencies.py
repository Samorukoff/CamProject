from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError
from project.database import get_db
from project.auth.models import User
from project.auth.repositories import get_user_by_name
from project.auth.utils.jwt import verify_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Определение авторизированного пользователя по токену
async def get_current_user(
    token: str = Depends(oauth2_scheme)
) -> User:
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = await get_user_by_name(payload["sub"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user