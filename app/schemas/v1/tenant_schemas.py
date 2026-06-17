from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.infrastructure.database.models.auth_models import TenantTypeEnum, SubscriptionPlanEnum
from uuid import UUID

class CreateTenantRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=255, pattern=r"^[a-z0-9-]+$")
    tenant_type: TenantTypeEnum = TenantTypeEnum.PERSONAL
    claimed_domain: Optional[str] = None


class UpdateTenantRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    claimed_domain: Optional[str] = None
    subscription_plan: Optional[SubscriptionPlanEnum] = None
    is_active: Optional[bool] = None
    settings: Optional[dict] = None


class TenantResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    tenant_type: str
    claimed_domain: Optional[str]
    is_domain_verified: bool
    subscription_plan: str
    is_active: bool
    settings: dict
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TenantListResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    tenant_type: str
    subscription_plan: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
