from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.infrastructure.database.models.auth_models import Tenant, SubscriptionPlanEnum
from typing import List, Optional
import uuid


class TenantRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        name: str,
        slug: str,
        tenant_type: str,
        claimed_domain: Optional[str] = None,
    ) -> Tenant:
        tenant = Tenant(
            id=uuid.uuid4(),
            name=name,
            slug=slug,
            tenant_type=tenant_type,
            claimed_domain=claimed_domain,
            is_active=True,
        )
        self.db.add(tenant)
        self.db.flush()
        return tenant

    def get_by_id(self, tenant_id: str) -> Optional[Tenant]:
        return self.db.query(Tenant).filter(Tenant.id == tenant_id).first()

    def get_by_slug(self, slug: str) -> Optional[Tenant]:
        return self.db.query(Tenant).filter(Tenant.slug == slug).first()

    def get_all(self, skip: int = 0, limit: int = 10) -> List[Tenant]:
        return (
            self.db.query(Tenant)
            .filter(Tenant.deleted_at.is_(None))
            .order_by(desc(Tenant.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update(
        self,
        tenant_id: str,
        name: Optional[str] = None,
        claimed_domain: Optional[str] = None,
        subscription_plan: Optional[str] = None,
        is_active: Optional[bool] = None,
        settings: Optional[dict] = None,
    ) -> Optional[Tenant]:
        tenant = self.get_by_id(tenant_id)
        if not tenant:
            return None

        if name:
            tenant.name = name
        if claimed_domain is not None:
            tenant.claimed_domain = claimed_domain
        if subscription_plan:
            tenant.subscription_plan = subscription_plan
        if is_active is not None:
            tenant.is_active = is_active
        if settings:
            tenant.settings = {**tenant.settings, **settings}

        self.db.flush()
        return tenant

    def delete(self, tenant_id: str) -> bool:
        tenant = self.get_by_id(tenant_id)
        if not tenant:
            return False

        self.db.delete(tenant)
        self.db.flush()
        return True

    def soft_delete(self, tenant_id: str) -> Optional[Tenant]:
        from sqlalchemy.sql import func

        tenant = self.get_by_id(tenant_id)
        if not tenant:
            return None

        tenant.deleted_at = func.now()
        self.db.flush()
        return tenant
