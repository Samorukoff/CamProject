from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class CompanyCreateIn(BaseModel):
    name: str = Field(min_length=2, max_length=128)


class CompanyOut(BaseModel):
    id: int
    name: str


class CompanyLoginIn(BaseModel):
    company_id: int
