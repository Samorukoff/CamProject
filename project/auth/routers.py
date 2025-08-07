from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from project.auth.utils.jwt import create_access_token, create_refresh_token
from project.auth.schemas import UserCreate, Token, RefreshRequest
from project.auth.services import register_user, authenticate_user, rotate_tokens

from project.core.config.logging.logger import logger

router = APIRouter()


@router.post("/auth/register", response_model=Token,
            summary="Регистрация")
async def register(user: UserCreate):
    logger.info(f"Register endpoint called for: {user.full_name}")
    new_user = await register_user(user)
    access_token = create_access_token({"sub": str(user.full_name)})
    refresh_token = create_refresh_token({"sub": str(user.full_name)})
    logger.info(f"User {new_user.id} registered and token issued")
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/auth/login", response_model=Token,
            summary="Авторизация")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    logger.info(f"Login attempt for user: {form_data.username}")
    auth_user = await authenticate_user(form_data.username, form_data.password)
    access_token = create_access_token({"sub": str(auth_user.full_name)})
    refresh_token = create_refresh_token({"sub": str(auth_user.full_name)})
    logger.info(f"User {auth_user.id} logged in successfully")
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/auth/refresh", response_model=Token, summary="Обновить токен")
async def refresh_token(data: RefreshRequest):
    return rotate_tokens(data.refresh_token)