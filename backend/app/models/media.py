import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Media(Base):
    __tablename__ = "media"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    original_filename: Mapped[str | None] = mapped_column(String(255))
    storage_key: Mapped[str] = mapped_column(String(500), nullable=False, unique=True, index=True)
    mime_type: Mapped[str] = mapped_column(String(64), nullable=False)
    file_size: Mapped[int | None] = mapped_column(Integer)
    width: Mapped[int | None] = mapped_column(Integer)
    height: Mapped[int | None] = mapped_column(Integer)
    title: Mapped[str | None] = mapped_column(String(255))
    alt_text: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    project_media: Mapped[list["ProjectMedia"]] = relationship(back_populates="media", cascade="all, delete-orphan")
