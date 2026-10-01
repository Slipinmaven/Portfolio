import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Technology(Base):
    __tablename__ = "technologies"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    short_description: Mapped[str | None] = mapped_column(String(500))
    category: Mapped[str] = mapped_column(String(32), default="other", server_default="other")
    icon: Mapped[str | None] = mapped_column(String(255))
    display_order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    project_technologies: Mapped[list["ProjectTechnology"]] = relationship(
        back_populates="technology",
        cascade="all, delete-orphan",
        order_by="ProjectTechnology.display_order",
    )
