from pydantic import BaseModel, EmailStr

# Схема для регистрации
class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    company_id: str

class AdminCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    company_name: str

# Схема для токена
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

# Схема для запроса с refresh токеном
class RefreshRequest(BaseModel):
    refresh_token: str
