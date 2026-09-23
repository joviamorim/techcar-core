import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from techcar_core.database import Base


class Role(Base):
    __tablename__ = "roles"
    __table_args__ = (
        # nome único dentro de cada tenant (ou entre os papéis globais, onde tenant_id é nulo)
        UniqueConstraint("tenant_id", "name", name="uq_roles_tenant_name"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    # nulo = papel padrão do sistema (ex.: owner, admin, member), disponível para todos os tenants
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=True,
    )
    name: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    tenant: Mapped["Tenant | None"] = relationship(back_populates="roles")
    memberships: Mapped[list["Membership"]] = relationship(back_populates="role")