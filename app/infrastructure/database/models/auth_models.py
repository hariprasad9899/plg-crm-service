from enum import Enum
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Enum as SqlEnum,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func
import uuid


class Base(DeclarativeBase):
    pass


class TenantTypeEnum(str, Enum):
    PERSONAL = "personal"
    ORGANIZATION = "organization"


class SubscriptionPlanEnum(str, Enum):
    FREE = "free"
    STARTER = "starter"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class MembershipRoleEnum(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class AuthProviderEnum(str, Enum):
    PASSWORD = "password"
    GOOGLE = "google"
    MICROSOFT = "microsoft"


class UserStatusEnum(str, Enum):
    ACTIVE = "active"
    INVITED = "invited"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class Tenant(Base):

    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    tenant_type: Mapped[TenantTypeEnum] = mapped_column(
        SqlEnum(TenantTypeEnum, name="tenant_type_enum"),
        nullable=False,
        default=TenantTypeEnum.PERSONAL,
        values_callable=lambda obj: [e.value for e in obj],
    )
    claimed_domain: Mapped[str | None] = mapped_column(String(255))
    is_domain_verified: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    subscription_plan: Mapped[SubscriptionPlanEnum] = mapped_column(
        SqlEnum(SubscriptionPlanEnum, name="subscription_plan_enum"),
        nullable=False,
        default=SubscriptionPlanEnum.FREE,
        values_callable=lambda obj: [e.value for e in obj],
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    settings: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    deleted_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))
    memberships = relationship(
        "TenantMembership", back_populates="tenant", cascade="all, delete-orphan"
    )
    workspaces = relationship(
        "Workspace", back_populates="tenant", cascade="all, delete-orphan"
    )
    sessions = relationship("Session", back_populates="tenant")
    __table_args__ = (
        CheckConstraint("slug ~ '^[a-z0-9-]+$'", name="ck_tenants_slug"),
        Index("idx_tenant_slug", "slug", unique=True),
        Index("idx_tenants_domain", "claimed_domain"),
        Index(
            "idx_unique_claimed_domain",
            func.lower(claimed_domain),
            unique=True,
            postgresql_where=claimed_domain.isnot(None),
        ),
    )


class User(Base):

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    full_name: Mapped[str | None] = mapped_column(String(255))
    primary_email: Mapped[str] = mapped_column(String(320), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_email_verified: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    last_login_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[UserStatusEnum] = mapped_column(
        SqlEnum(
            UserStatusEnum,
            name="user_status_enum",
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
        default=UserStatusEnum.ACTIVE,
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    deleted_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))
    auth_identities = relationship(
        "AuthIdentity", back_populates="user", cascade="all, delete-orphan"
    )
    memberships = relationship(
        "TenantMembership",
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="TenantMembership.user_id",
    )
    refresh_tokens = relationship(
        "RefreshToken", back_populates="user", cascade="all, delete-orphan"
    )
    sessions = relationship(
        "Session", back_populates="user", cascade="all, delete-orphan"
    )
    __table_args__ = (Index("idx_user_email", func.lower(primary_email), unique=True),)


class AuthIdentity(Base):

    __tablename__ = "auth_identities"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    provider: Mapped[AuthProviderEnum] = mapped_column(
        SqlEnum(
            AuthProviderEnum,
            name="auth_provider_enum",
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
    )
    provider_user_id: Mapped[str | None] = mapped_column(Text)
    provider_email: Mapped[str] = mapped_column(Text, nullable=False)
    password_hash: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    user = relationship("User", back_populates="auth_identities")
    __table_args__ = (
        CheckConstraint(
            """
            (
                provider = 'password'
                AND password_hash IS NOT NULL
            )
            OR
            (
                provider != 'password'
            )
            """,
            name="ck_password_hash_required",
        ),
        Index("idx_auth_user", "user_id"),
        Index(
            "idx_provider_identity",
            "provider",
            "provider_user_id",
            unique=True,
            postgresql_where=text("provider_user_id IS NOT NULL"),
        ),
        Index(
            "idx_password_email",
            func.lower(provider_email),
            unique=True,
            postgresql_where=text("provider = 'password'"),
        ),
    )


class RefreshToken(Base):

    __tablename__ = "refresh_tokens"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    token_hash: Mapped[str] = mapped_column(Text, nullable=False)
    expires_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    revoked_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    user = relationship("User", back_populates="refresh_tokens")
    __table_args__ = (Index("idx_refresh_user", "user_id"),)


class TenantMembership(Base):

    __tablename__ = "tenant_memberships"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[MembershipRoleEnum] = mapped_column(
        SqlEnum(MembershipRoleEnum, name="membership_role_enum"),
        nullable=False,
        default=MembershipRoleEnum.MEMBER,
        values_callable=lambda obj: [e.value for e in obj],
    )
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    joined_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    invited_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    tenant = relationship("Tenant", back_populates="memberships")
    user = relationship("User", back_populates="memberships", foreign_keys=[user_id])
    __table_args__ = (
        UniqueConstraint("tenant_id", "user_id", name="uq_tenant_user"),
        Index("idx_membership_user", "user_id"),
        Index("idx_membership_tenant", "tenant_id"),
        Index("idx_membership_role", "role"),
    )


class Workspace(Base):

    __tablename__ = "workspaces"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    tenant = relationship("Tenant", back_populates="workspaces")
    __table_args__ = (Index("idx_workspace_tenant", "tenant_id"),)


class Session(Base):

    __tablename__ = "sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE")
    )
    refresh_token_hash: Mapped[str] = mapped_column(Text, nullable=False)
    ip_address: Mapped[str | None] = mapped_column(INET)
    user_agent: Mapped[str | None] = mapped_column(Text)
    device_name: Mapped[str | None] = mapped_column(Text)
    expires_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    revoked_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    user = relationship("User", back_populates="sessions")
    tenant = relationship("Tenant", back_populates="sessions")
    __table_args__ = (
        Index("idx_sessions_user", "user_id"),
        Index("idx_sessions_tenant", "tenant_id"),
        Index("idx_sessions_revoked", "revoked_at"),
    )
