from fastapi import HTTPException, status
from project.auth.models import User
from project.auth.schemas import UserCreate, AdminCreate
from project.auth.repositories import (
    register_user_in_db,
    get_user_by_name,
    get_company_by_name,
    create_company
)
from passlib.context import CryptContext
from project.auth.utils.jwt import (
    verify_refresh_token,
    create_access_token,
    create_refresh_token
)

from project.core.config.logging.logger import logger

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Хеширование пароля
def hash_password(password: str) -> str:
    logger.debug("Hashing user password")
    return pwd_context.hash(password)

# Верификация пароля (проверка на соответствие хешу)
def verify_password(plain: str, hashed: str):
    result = pwd_context.verify(plain, hashed)
    logger.debug(f"Password verification result: {result}")
    return result

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

# Регистрация админа
async def register_admin(user: AdminCreate):
    logger.info(f"Attempting to register company admin: {user.full_name}")

    # Проверяем — есть ли уже такая компания
    company = await get_company_by_name(user.company_name)
    if company:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company already exists"
        )

    # Создаём новую компанию
    company = await create_company(user.company_name)

    # Регистрируем админа, привязанного к компании
    new_user = User(
        full_name=user.full_name,
        email=user.email,
        password=hash_password(user.password),
        is_admin=True,
        company_id=company.id
    )

    return await register_user_in_db(new_user)

# Авторизация пользователя
async def authenticate_user(full_name: str, password: str):
    logger.debug(f"Authenticating user: {full_name}")
    user = await get_user_by_name(full_name)

    if not user or not verify_password(password, user.password):
        logger.warning(f"Failed login attempt for user: {full_name}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    logger.info(f"User {user.id} authenticated successfully")
    return user

# Проверка refresh токена
def rotate_tokens(refresh_token: str) -> dict:
    if not refresh_token:
        raise HTTPException(status_code=400, detail="Missing refresh token")

    payload = verify_refresh_token(refresh_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=401, detail="Invalid payload")

    return {
        "access_token": create_access_token({"sub": sub}),
        "refresh_token": create_refresh_token({"sub": sub}),
        "token_type": "bearer",
        "action": "stay",
        "to": "/"
    }