from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from project.auth.utils.jwt import create_access_token
from project.auth.schemas import UserCreate, Token
from project.auth.dependencies import get_db
from project.auth.services import register_user, authenticate_user
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.post("/auth/register", response_model=Token,
            summary="Регистрация")
async def register(user: UserCreate):
    new_user = await register_user(user)
    token = create_access_token({"sub": str(new_user.full_name)})
    return {
        "access_token": token,
        "token_type": "bearer",
        "action": "redirect",
        "to": "/"
    }

@router.post("/auth/login", response_model=Token,
            summary="Авторизация")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    auth_user = await authenticate_user(form_data.username, form_data.password)
    if not auth_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": str(auth_user.full_name)})
    return {
        "access_token": token,
        "token_type": "bearer",
        "action": "redirect",
        "to": "/"
    }