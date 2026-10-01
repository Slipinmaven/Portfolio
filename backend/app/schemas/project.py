import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class TechnologySummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    category: str | None = None
    icon: str | None = None
    display_order: int = 0
    is_featured: bool = False


class ProjectFeatureSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    description: str | None = None
    display_order: int = 0


class MediaAssetSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    storage_key: str
    mime_type: str
    title: str | None = None
    alt_text: str | None = None
    width: int | None = None
    height: int | None = None


class ProjectMediaSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    type: str
    title: str | None = None
    caption: str | None = None
    alt_text: str | None = None
    display_order: int = 0
    is_cover: bool = False
    media: MediaAssetSchema


class ProjectBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    slug: str | None = Field(default=None, min_length=1, max_length=255)
    short_description: str | None = Field(default=None, max_length=500)
    description: str | None = None
    problem: str | None = None
    solution: str | None = None
    technical_details: str | None = None
    technical_decisions: str | None = None
    challenges: str | None = None
    outcome: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    status: Literal["planning", "in_progress", "completed", "archived"] = "planning"
    publication_status: Literal["draft", "published"] = "draft"
    is_featured: bool = False
    display_order: int = 0
    github_url: HttpUrl | str | None = None
    live_url: HttpUrl | str | None = None
    meta_title: str | None = Field(default=None, max_length=255)
    meta_description: str | None = Field(default=None, max_length=500)


class ProjectCreate(ProjectBase):
    technology_ids: list[uuid.UUID] = Field(default_factory=list)
    feature_titles: list[str] = Field(default_factory=list)


class ProjectUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    slug: str | None = None
    short_description: str | None = Field(default=None, max_length=500)
    description: str | None = None
    problem: str | None = None
    solution: str | None = None
    technical_details: str | None = None
    technical_decisions: str | None = None
    challenges: str | None = None
    outcome: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    status: Literal["planning", "in_progress", "completed", "archived"] | None = None
    publication_status: Literal["draft", "published"] | None = None
    is_featured: bool | None = None
    display_order: int | None = None
    github_url: HttpUrl | str | None = None
    live_url: HttpUrl | str | None = None
    meta_title: str | None = None
    meta_description: str | None = None


class ProjectAdminResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    slug: str
    short_description: str | None = None
    description: str | None = None
    status: str
    publication_status: str
    is_featured: bool
    display_order: int
    github_url: str | None = None
    live_url: str | None = None
    published_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    features: list[ProjectFeatureSchema] = []
    technologies: list[TechnologySummary] = []
    media: list[ProjectMediaSchema] = []


class ProjectPublicResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    slug: str
    short_description: str | None = None
    description: str | None = None
    problem: str | None = None
    solution: str | None = None
    technical_details: str | None = None
    technical_decisions: str | None = None
    challenges: str | None = None
    outcome: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    status: str
    github_url: str | None = None
    live_url: str | None = None
    technologies: list[TechnologySummary] = []
    features: list[ProjectFeatureSchema] = []
    media: list[ProjectMediaSchema] = []


class TechnologyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    slug: str | None = Field(default=None, min_length=1, max_length=255)
    short_description: str | None = Field(default=None, max_length=500)
    category: str = "other"
    icon: str | None = None
    display_order: int = 0
    is_featured: bool = False


class TechnologyUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    slug: str | None = None
    short_description: str | None = Field(default=None, max_length=500)
    category: str | None = None
    icon: str | None = None
    display_order: int | None = None
    is_featured: bool | None = None


class TechnologyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    short_description: str | None = None
    category: str
    icon: str | None = None
    display_order: int
    is_featured: bool
    created_at: datetime
    updated_at: datetime
