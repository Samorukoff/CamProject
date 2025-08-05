from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from project.auth.utils.jwt import create_access_token
from project.auth.schemas import UserCreate, Token
from project.auth.services import register_user, authenticate_user

from project.core.config.logging.logger import logger

router = APIRouter()


@router.post("/auth/register", response_model=Token,
            summary="Регистрация")
async def register(user: UserCreate):
    logger.info(f"Register endpoint called for: {user.full_name}")
    new_user = await register_user(user)
    token = create_access_token({"sub": str(new_user.full_name)})
    logger.info(f"User {new_user.id} registered and token issued")
    return {
        "access_token": token,
        "token_type": "bearer",
        "action": "redirect",
        "to": "/"
    }


@router.post("/auth/login", response_model=Token,
            summary="Авторизация")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    logger.info(f"Login attempt for user: {form_data.username}")
    auth_user = await authenticate_user(form_data.username, form_data.password)
    token = create_access_token({"sub": str(auth_user.full_name)})
    logger.info(f"User {auth_user.id} logged in successfully")
    return {
        "access_token": token,
        "token_type": "bearer",
        "action": "redirect",
        "to": "/"
    }