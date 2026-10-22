from typing import Optional, List
from pydantic import BaseModel, Field

class LegacyPlanBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=150, example="Comprehensive Digital Asset & Crypto Succession Plan")
    trigger_condition: str = Field(..., example="Legal Death Certificate Verification")
    status: str = Field(default="Active", example="Active")
    notes: Optional[str] = Field(None, example="Release Bitcoin keys to Julian and Photo Archive to Clara via Attorney Sterling.")

class LegacyPlanCreate(LegacyPlanBase):
    id: Optional[str] = Field(None, example="pln_001")
    user_id: Optional[str] = Field(None, example="usr_001")
    asset_ids: Optional[List[str]] = Field(default_factory=list)
    nominee_ids: Optional[List[str]] = Field(default_factory=list)
    executor_ids: Optional[List[str]] = Field(default_factory=list)
    release_id: Optional[str] = Field(None, example="rel_001")

class LegacyPlanUpdate(BaseModel):
    title: Optional[str] = None
    trigger_condition: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    user_id: Optional[str] = None
    asset_ids: Optional[List[str]] = None
    nominee_ids: Optional[List[str]] = None
    executor_ids: Optional[List[str]] = None
    release_id: Optional[str] = None

class LegacyPlanResponse(LegacyPlanBase):
    id: str
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    included_assets: Optional[List[str]] = []
    assigned_nominees: Optional[List[str]] = []
    overseeing_executors: Optional[List[str]] = []
    release_id: Optional[str] = None
    release_date: Optional[str] = None
    created_at: Optional[str] = None
