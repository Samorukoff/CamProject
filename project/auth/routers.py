from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from project.auth.utils.jwt import create_access_token, create_refresh_token
from project.auth.schemas import UserCreate, LoginByEmail, Token, RefreshRequest
from project.auth.services import register_user, authenticate_user, rotate_tokens

from project.core.config.logging.logger import logger

router = APIRouter()


@router.post("/auth/register",
            summary="Регистрация")
async def register(user: UserCreate):
    logger.info(f"Register endpoint called for: {user.full_name}")
    new_user = await register_user(user)
    logger.info(f"Company admin {new_user.id} registered")
    return new_user


@router.post("/auth/login", response_model=Token, summary="Авторизация")
async def login(body: LoginByEmail):
    logger.info(f"Login attempt for user: {body.email}")
    token_pair = await authenticate_user(body.email, body.password)
    logger.info("User logged in successfully")
    return token_pair


@router.post("/auth/refresh", response_model=Token, summary="Обновить токен")
async def refresh_token(data: RefreshRequest):
    refresh_raw = data.refresh_token.get_secret_value()
    return await rotate_tokens(refresh_raw)