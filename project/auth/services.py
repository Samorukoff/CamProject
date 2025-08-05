from fastapi import HTTPException, status
from project.auth.models import User
from project.auth.schemas import UserCreate
from project.auth.repositories import register_user_in_db, get_user_by_name
from passlib.context import CryptContext

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
