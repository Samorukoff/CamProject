from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, Literal


class EmployeeOut(BaseModel):
    user_id: int
    email: EmailStr
    full_name: Optional[str] = None
    role: Literal["admin", "employee"]
    is_owner: bool

class EmployeeAddIn(BaseModel):
    user_id: int
    role: Literal["admin", "employee"] = "employee"
    is_owner: bool = False

class EmployeeDeleteIn(BaseModel):
    user_id: int

class EmployeeLookupOut(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: int
    email: EmailStr
    full_name: Optional[str] = None