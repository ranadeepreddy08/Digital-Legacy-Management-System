from typing import Optional, List
from pydantic import BaseModel, Field

class DigitalAssetBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=150, example="Cold Storage Bitcoin Wallet")
    asset_type: str = Field(..., example="Cryptocurrency")
    access_info_encrypted_hint: str = Field(
        ...,
        min_length=3,
        example="Hardware Ledger seed phrase stored in Safe Deposit Box #402"
    )
    priority: str = Field(default="Medium", example="Critical")
    estimated_value: Optional[str] = Field(None, example="$125,000 USD")

class DigitalAssetCreate(DigitalAssetBase):
    id: Optional[str] = Field(None, example="ast_001")
    owner_id: Optional[str] = Field(None, example="usr_001")
    designated_nominee_id: Optional[str] = Field(None, example="nom_001")
    nominee_share_pct: Optional[int] = Field(100, ge=1, le=100)
    managing_executor_id: Optional[str] = Field(None, example="exe_001")

class DigitalAssetUpdate(BaseModel):
    title: Optional[str] = None
    asset_type: Optional[str] = None
    access_info_encrypted_hint: Optional[str] = None
    priority: Optional[str] = None
    estimated_value: Optional[str] = None
    owner_id: Optional[str] = None
    designated_nominee_id: Optional[str] = None
    nominee_share_pct: Optional[int] = None
    managing_executor_id: Optional[str] = None

class DigitalAssetResponse(DigitalAssetBase):
    id: str
    owner_id: Optional[str] = None
    owner_name: Optional[str] = None
    designated_nominee_name: Optional[str] = None
    designated_nominee_id: Optional[str] = None
    nominee_share_pct: Optional[int] = None
    managing_executor_name: Optional[str] = None
    managing_executor_id: Optional[str] = None
    plan_title: Optional[str] = None
    created_at: Optional[str] = None
