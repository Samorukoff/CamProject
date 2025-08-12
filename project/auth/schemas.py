from typing import Annotated, Literal
from pydantic import (
    BaseModel,
    EmailStr,
    SecretStr,
    field_validator,
    StringConstraints,
    ConfigDict,
)

# Общие типы
NameStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=128)]

# Регистрация
class UserCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")  # запрет лишних полей

    full_name: NameStr
    email: EmailStr
    password: SecretStr  # секрет, не утечёт в логи при сериализации

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().casefold()

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: SecretStr) -> SecretStr:
        pwd = v.get_secret_value()
        if not (8 <= len(pwd) <= 128):
            raise ValueError("Password length must be 8..128")
        if not any(ch.isalpha() for ch in pwd) or not any(ch.isdigit() for ch in pwd):
            raise ValueError("Password must contain letters and digits")
        return v

# Авторизация (логин)
class LoginByEmail(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    password: SecretStr

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().casefold()

# Токены (ответ)
class Token(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [{
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
            }]
        },
    )

    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"

# Обновление по refresh-токену (запрос)
class RefreshRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    refresh_token: SecretStr
