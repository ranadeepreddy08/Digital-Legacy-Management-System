import re
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator

EMAIL_REGEX = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

class ExecutorBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, example="Robert Sterling, Esq.")
    email: str = Field(..., example="sterling@heritage-law.com")
    phone: Optional[str] = Field(None, example="+1-555-0301")
    verification_status: str = Field(default="Verified Notary", example="Verified Notary & Attorney")
    role_description: Optional[str] = Field(None, example="Legal Executor & Estate Counsel")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not re.match(EMAIL_REGEX, v):
            raise ValueError("Invalid email format.")
        return v.lower().strip()

class ExecutorCreate(ExecutorBase):
    id: Optional[str] = Field(None, example="exe_001")
    user_id: Optional[str] = Field(None, example="usr_001")
    authorized_asset_ids: Optional[List[str]] = Field(default_factory=list)

class ExecutorUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    verification_status: Optional[str] = None
    role_description: Optional[str] = None
    user_id: Optional[str] = None
    authorized_asset_ids: Optional[List[str]] = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not re.match(EMAIL_REGEX, v):
                raise ValueError("Invalid email format.")
            return v.lower().strip()
        return v

class ExecutorResponse(ExecutorBase):
    id: str
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    managed_assets: Optional[List[str]] = []
    created_at: Optional[str] = None
