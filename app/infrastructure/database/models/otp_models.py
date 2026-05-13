import enum
import uuid
from datetime import datetime
from sqlalchemy import ForeignKey, Enum as SqlEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.database.base import Base
from sqlalchemy.sql import func


class OTPPurposeEnum(str, enum.Enum):
    EMAIL_VERIFICATION = "email_verification"
    PASSWORD_RESET = "password_reset"
    LOGIN = "login"


class AuthOTP(Base):
    __tablename__ = "auth_otps"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    auth_identity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth_identities.id", ondelete="CASCADE"),
        nullable=False,
    )
    otp_hash: Mapped[str] = mapped_column(
        nullable=False,
    )
    purpose: Mapped[OTPPurposeEnum] = mapped_column(
        SqlEnum(
            OTPPurposeEnum,
            name="otp_purpose_enum",
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
    )
    expires_at: Mapped[datetime] = mapped_column(nullable=False)
    consumed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    attempt_count: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
    )
    auth_identity: Mapped["AuthIdentity"] = relationship(
        back_populates="otps",
    )
