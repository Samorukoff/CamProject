from sqlalchemy.ext.asyncio import AsyncSession
from project.auth.models import User
from project.auth.schemas import UserCreate
from project.auth.repositories import register_user_in_db, get_user_by_name
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Хеширование пароля
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Верификация пароля (проверка на соответствие хешу)
def verify_password(plain: str, hashed: str):
    return pwd_context.verify(plain, hashed)

# Регистрация пользователя
async def register_user(user: UserCreate):
    new_user = User(
        full_name=user.full_name,
        email=user.email,
        password=hash_password(user.password)
    )
    return await register_user_in_db(new_user)

#Авторизация пользователя
async def authenticate_user(full_name: str, password: str):
    user = await get_user_by_name(full_name)
    if not user or not verify_password(password, user.password):
        return None
    return user
