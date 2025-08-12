from fastapi import HTTPException, status
from project.auth.models import User
from project.auth.schemas import UserCreate, UserCreate, Token
from project.auth.repositories import (
    register_user_in_db,
    get_user_by_email,
)
from pydantic import SecretStr
from passlib.context import CryptContext
from project.auth.utils.jwt import (
    verify_refresh_token,
    create_access_token,
    create_refresh_token
)

from project.core.config.logging.logger import logger

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def _to_plain(p: str | SecretStr) -> str:
    return p.get_secret_value() if isinstance(p, SecretStr) else p

# Хеширование пароля
def hash_password(password: str | SecretStr) -> str:
    return pwd_context.hash(_to_plain(password))

# Верификация пароля (проверка на соответствие хешу)
def verify_password(plain: str | SecretStr, hashed: str) -> bool:
    return pwd_context.verify(_to_plain(plain), hashed)


# Регистрация пользователя
async def register_user(user: UserCreate):
    logger.info(f"Attempting to register user: {user.full_name}")
    new_user = User(
        full_name=user.full_name,
        email=user.email,
        password=hash_password(user.password)
    )
    saved_user = await register_user_in_db(new_user)
    logger.info(f"User {saved_user.id} registered successfully")
    return saved_user

# Авторизация пользователя + выдача токенов
async def authenticate_user(email: str, password: str | SecretStr) -> Token:
    logger.debug(f"Authenticating user: {email}")
    user = await get_user_by_email(email)

    if not user or not verify_password(password, user.password):
        logger.warning(f"Failed login attempt for user: {email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    logger.info(f"User {user.id} authenticated successfully")

    access = create_access_token({"sub": str(user.id), "type": "access"})
    refresh = create_refresh_token({"sub": str(user.id), "type": "refresh"})

    logger.info(f"Issued tokens for user_id={user.id}")
    return Token(access_token=access, refresh_token=refresh)

# Проверка refresh токена
async def rotate_tokens(refresh_token: str) -> Token:
    payload = verify_refresh_token(refresh_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    sub = str(payload["sub"])
    cid = payload.get("cid")
    access = create_access_token({"sub": sub, "cid": cid, "type": "access"})
    refresh = create_refresh_token({"sub": sub, "cid": cid, "type": "refresh"})
    return Token(access_token=access, refresh_token=refresh)