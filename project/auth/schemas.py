from pydantic import BaseModel, EmailStr

# Схема для регистрации
class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str

# Схема для токена
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"