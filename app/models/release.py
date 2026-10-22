from typing import Optional, List
from pydantic import BaseModel, Field

class ScheduledReleaseBase(BaseModel):
    release_date: str = Field(..., example="2026-12-01T00:00:00Z")
    status: str = Field(default="Scheduled", example="Scheduled")
    notification_method: str = Field(default="Encrypted Email", example="Encrypted Email + SMS OTP")
    notes: Optional[str] = Field(None, example="Automated transfer trigger upon non-response to annual heartbeat ping")

class ScheduledReleaseCreate(ScheduledReleaseBase):
    id: Optional[str] = Field(None, example="rel_001")
    plan_id: Optional[str] = Field(None, example="pln_001")
    asset_id: Optional[str] = Field(None, example="ast_001")

class ScheduledReleaseUpdate(BaseModel):
    release_date: Optional[str] = None
    status: Optional[str] = None
    notification_method: Optional[str] = None
    notes: Optional[str] = None
    plan_id: Optional[str] = None
    asset_id: Optional[str] = None

class ScheduledReleaseResponse(ScheduledReleaseBase):
    id: str
    plan_id: Optional[str] = None
    plan_title: Optional[str] = None
    asset_id: Optional[str] = None
    asset_title: Optional[str] = None
    created_at: Optional[str] = None
