from fastapi import APIRouter, Depends, HTTPException, Query
from app.schemas.v1.tenant_schemas import (
    CreateTenantRequest,
    UpdateTenantRequest,
    TenantResponse,
    TenantListResponse,
)
from app.domain.services.tenant_service import TenantService
from app.dependencies.tenant_dependencies import get_tenant_service
from typing import List

router = APIRouter(prefix="/tenants", tags=["tenants"])


@router.post("", response_model=TenantResponse, status_code=201)
def create_tenant(
    data: CreateTenantRequest,
    service: TenantService = Depends(get_tenant_service),
):
    print(data.tenant_type)
    print(data.tenant_type.value)
    print(type(data.tenant_type))
    """Create a new tenant"""
    tenant = service.create_tenant(
        name=data.name,
        slug=data.slug,
        tenant_type=data.tenant_type.value,
        claimed_domain=data.claimed_domain,
    )
    return tenant


@router.get("", response_model=List[TenantListResponse])
def list_tenants(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    service: TenantService = Depends(get_tenant_service),
):
    """List all tenants with pagination"""
    tenants = service.list_tenants(skip=skip, limit=limit)
    return tenants


@router.get("/{tenant_id}", response_model=TenantResponse)
def get_tenant(
    tenant_id: str,
    service: TenantService = Depends(get_tenant_service),
):
    """Get tenant by ID"""
    tenant = service.get_tenant(tenant_id)
    return tenant


@router.get("/slug/{slug}", response_model=TenantResponse)
def get_tenant_by_slug(
    slug: str,
    service: TenantService = Depends(get_tenant_service),
):
    """Get tenant by slug"""
    tenant = service.get_tenant_by_slug(slug)
    return tenant


@router.put("/{tenant_id}", response_model=TenantResponse)
def update_tenant(
    tenant_id: str,
    data: UpdateTenantRequest,
    service: TenantService = Depends(get_tenant_service),
):
    """Update tenant"""
    tenant = service.update_tenant(
        tenant_id=tenant_id,
        name=data.name,
        claimed_domain=data.claimed_domain,
        subscription_plan=data.subscription_plan.value if data.subscription_plan else None,
        is_active=data.is_active,
        settings=data.settings,
    )
    return tenant


@router.delete("/{tenant_id}", status_code=200)
def delete_tenant(
    tenant_id: str,
    service: TenantService = Depends(get_tenant_service),
):
    """Permanently delete a tenant"""
    service.delete_tenant(tenant_id)
    return {"message": "Tenant deleted successfully"}


@router.post("/{tenant_id}/soft-delete")
def soft_delete_tenant(
    tenant_id: str,
    service: TenantService = Depends(get_tenant_service),
):
    """Soft delete a tenant (mark as deleted without removing data)"""
    return service.soft_delete_tenant(tenant_id)
