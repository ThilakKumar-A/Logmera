from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class LogCreate(BaseModel):
    project_id: str = Field(min_length=1, max_length=255)
    prompt: str = Field(min_length=1)
    response: str = Field(min_length=1)
    model: str = Field(min_length=1, max_length=255)
    latency_ms: int | None = Field(default=None, ge=0)
    status: str | None = Field(default=None, max_length=64)


class LogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: str
    prompt: str
    response: str
    model: str
    latency_ms: int | None
    status: str | None
    created_at: datetime


class HealthResponse(BaseModel):
    status: str
