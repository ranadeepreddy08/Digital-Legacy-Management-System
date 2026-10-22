import re
from typing import Optional
from pydantic import BaseModel, Field, field_validator

EMAIL_REGEX = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, example="Eleanor Vance")
    email: str = Field(..., example="eleanor.vance@legacyvault.io")
    phone: Optional[str] = Field(None, max_length=25, example="+1-555-0101")
    status: str = Field(default="Active", example="Active")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not re.match(EMAIL_REGEX, v):
            raise ValueError("Invalid email format. Must contain '@' and a domain.")
        return v.lower().strip()

class UserCreate(UserBase):
    id: Optional[str] = Field(None, example="usr_001")

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[str] = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not re.match(EMAIL_REGEX, v):
                raise ValueError("Invalid email format.")
            return v.lower().strip()
        return v

class UserResponse(UserBase):
    id: str
    created_at: Optional[str] = None
    asset_count: Optional[int] = 0
    nominee_count: Optional[int] = 0
    plan_count: Optional[int] = 0
