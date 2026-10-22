import re
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator

EMAIL_REGEX = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

class NomineeBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, example="Julian Vance")
    relationship: str = Field(..., example="Spouse")
    email: str = Field(..., example="julian.vance@gmail.com")
    phone: Optional[str] = Field(None, example="+1-555-0201")
    allocation_percentage: int = Field(default=100, ge=1, le=100, example=100)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not re.match(EMAIL_REGEX, v):
            raise ValueError("Invalid email format.")
        return v.lower().strip()

class NomineeCreate(NomineeBase):
    id: Optional[str] = Field(None, example="nom_001")
    user_id: Optional[str] = Field(None, example="usr_001")
    designated_asset_id: Optional[str] = Field(None, example="ast_001")

class NomineeUpdate(BaseModel):
    name: Optional[str] = None
    relationship: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    allocation_percentage: Optional[int] = Field(None, ge=1, le=100)
    user_id: Optional[str] = None
    designated_asset_id: Optional[str] = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not re.match(EMAIL_REGEX, v):
                raise ValueError("Invalid email format.")
            return v.lower().strip()
        return v

class NomineeResponse(NomineeBase):
    id: str
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    designated_assets: Optional[List[str]] = []
    created_at: Optional[str] = None
