from app.infrastructure.database.repositories.tenant_repository import TenantRepository
from app.core.exceptions.base import AppException
from app.core.exceptions.error_catalog import NOT_FOUND
from typing import Optional, List


class TenantService:
    def __init__(self, tenant_repo: TenantRepository):
        self.tenant_repo = tenant_repo

    def create_tenant(
        self,
        name: str,
        slug: str,
        tenant_type: str,
        claimed_domain: Optional[str] = None,
    ):
    
        tenant = self.tenant_repo.create(
            name=name,
            slug=slug,
            tenant_type=tenant_type,
            claimed_domain=claimed_domain,
        )
        self.tenant_repo.db.commit()
        return tenant

    def get_tenant(self, tenant_id: str):
        tenant = self.tenant_repo.get_by_id(tenant_id)
        if not tenant:
            raise AppException(NOT_FOUND)
        return tenant

    def get_tenant_by_slug(self, slug: str):
        tenant = self.tenant_repo.get_by_slug(slug)
        if not tenant:
            raise AppException(NOT_FOUND)
        return tenant

    def list_tenants(self, skip: int = 0, limit: int = 10) -> List:
        return self.tenant_repo.get_all(skip=skip, limit=limit)

    def update_tenant(
        self,
        tenant_id: str,
        name: Optional[str] = None,
        claimed_domain: Optional[str] = None,
        subscription_plan: Optional[str] = None,
        is_active: Optional[bool] = None,
        settings: Optional[dict] = None,
    ):
        tenant = self.tenant_repo.update(
            tenant_id=tenant_id,
            name=name,
            claimed_domain=claimed_domain,
            subscription_plan=subscription_plan,
            is_active=is_active,
            settings=settings,
        )
        if not tenant:
            raise AppException(NOT_FOUND)
        self.tenant_repo.db.commit()
        return tenant

    def delete_tenant(self, tenant_id: str):
        success = self.tenant_repo.delete(tenant_id)
        if not success:
            raise AppException(NOT_FOUND)
        self.tenant_repo.db.commit()
        return {"message": "Tenant deleted successfully"}

    def soft_delete_tenant(self, tenant_id: str):
        tenant = self.tenant_repo.soft_delete(tenant_id)
        if not tenant:
            raise AppException(NOT_FOUND)
        self.tenant_repo.db.commit()
        return {"message": "Tenant soft deleted successfully"}
