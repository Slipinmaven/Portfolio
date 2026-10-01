import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)

    short_description: Mapped[str | None] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(Text)
    problem: Mapped[str | None] = mapped_column(Text)
    solution: Mapped[str | None] = mapped_column(Text)
    technical_details: Mapped[str | None] = mapped_column(Text)
    technical_decisions: Mapped[str | None] = mapped_column(Text)
    challenges: Mapped[str | None] = mapped_column(Text)
    outcome: Mapped[str | None] = mapped_column(Text)

    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    status: Mapped[str] = mapped_column(String(32), default="planning", server_default="planning")
    publication_status: Mapped[str] = mapped_column(String(32), default="draft", server_default="draft")

    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    display_order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    github_url: Mapped[str | None] = mapped_column(String(2048))
    live_url: Mapped[str | None] = mapped_column(String(2048))

    meta_title: Mapped[str | None] = mapped_column(String(255))
    meta_description: Mapped[str | None] = mapped_column(String(500))

    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    features: Mapped[list["ProjectFeature"]] = relationship(back_populates="project", cascade="all, delete-orphan", order_by="ProjectFeature.display_order")
    project_technologies: Mapped[list["ProjectTechnology"]] = relationship(back_populates="project", cascade="all, delete-orphan", order_by="ProjectTechnology.display_order")
    project_media: Mapped[list["ProjectMedia"]] = relationship(back_populates="project", cascade="all, delete-orphan", order_by="ProjectMedia.display_order")

    @property
    def technologies(self):
        return [association.technology for association in self.project_technologies]

    @property
    def media(self):
        return self.project_media


class ProjectFeature(Base):
    __tablename__ = "project_features"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    display_order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    project: Mapped["Project"] = relationship(back_populates="features")


class ProjectTechnology(Base):
    __tablename__ = "project_technologies"
    __table_args__ = (UniqueConstraint("project_id", "technology_id", name="uq_project_technology_pair"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    technology_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("technologies.id", ondelete="CASCADE"), nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    project: Mapped["Project"] = relationship(back_populates="project_technologies")
    technology: Mapped["Technology"] = relationship(back_populates="project_technologies")


class ProjectMedia(Base):
    __tablename__ = "project_media"
    __table_args__ = (
        UniqueConstraint("project_id", "media_id", name="uq_project_media_pair"),
        Index("uq_project_media_cover", "project_id", unique=True, sqlite_where=text("is_cover"), postgresql_where=text("is_cover")),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    media_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("media.id", ondelete="CASCADE"), nullable=False)
    type: Mapped[str] = mapped_column(String(32), default="other", server_default="other")
    title: Mapped[str | None] = mapped_column(String(255))
    caption: Mapped[str | None] = mapped_column(Text)
    alt_text: Mapped[str | None] = mapped_column(String(500))
    display_order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    is_cover: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    project: Mapped["Project"] = relationship(back_populates="project_media")
    media: Mapped["Media"] = relationship(back_populates="project_media")
