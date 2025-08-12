from jose import JWTError, jwt
from typing import Any, Optional
from datetime import datetime, timedelta
from project.auth.utils.config import security_settings


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=security_settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, security_settings.SECRET_KEY, algorithm=security_settings.ALGORITHM)


def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, security_settings.SECRET_KEY, algorithms=[security_settings.ALGORITHM])
        return payload
    except JWTError:
        return None
    

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(days=security_settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, security_settings.SECRET_KEY, algorithm=security_settings.ALGORITHM)


def verify_refresh_token(token: str) -> Optional[dict[str, Any]]:
    try:
        payload = jwt.decode(
            token,
            security_settings.SECRET_KEY,
            algorithms=[security_settings.ALGORITHM],
            options={"verify_aud": False},  # если не используешь aud
        )
    except JWTError:
        return None  # невалидный/просроченный/подпись не сошлась

    # должен быть именно refresh
    if payload.get("type") != "refresh":
        return None

    # обязательные клеймы
    if not payload.get("sub"):  # id пользователя
        return None

    return payload