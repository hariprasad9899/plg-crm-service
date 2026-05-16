from fastapi import Depends
from sqlalchemy.orm import Session
from app.infrastructure.database.session import get_db
from app.infrastructure.database.repositories.tenant_repository import TenantRepository
from app.domain.services.tenant_service import TenantService


def get_tenant_repository(db: Session = Depends(get_db)) -> TenantRepository:
    return TenantRepository(db)


def get_tenant_service(
    tenant_repo: TenantRepository = Depends(get_tenant_repository),
) -> TenantService:
    return TenantService(tenant_repo)
