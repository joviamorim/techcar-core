import enum
import uuid
from datetime import datetime

from sqlalchemy import Enum, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from techcar_core.database import Base


class MembershipStatus(str, enum.Enum):
    ACTIVE = "active"
    INVITED = "invited"
    SUSPENDED = "suspended"


class Membership(Base):
    __tablename__ = "memberships"
    __table_args__ = (
        # um usuário só pode ter um vínculo por tenant
        UniqueConstraint("user_id", "tenant_id", name="uq_memberships_user_tenant"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"),
    )
    role_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("roles.id", ondelete="RESTRICT"),
    )
    status: Mapped[MembershipStatus] = mapped_column(
        Enum(MembershipStatus, name="membership_status"),
        default=MembershipStatus.INVITED,
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="memberships")
    tenant: Mapped["Tenant"] = relationship(back_populates="memberships")
    role: Mapped["Role"] = relationship(back_populates="memberships")