from datetime import datetime
from pydantic import BaseModel, field_validator
from typing import Optional


class PostBase(BaseModel):
    content: str


class PostCreate(PostBase):
    status: Optional[str] = None
    scheduled_date: Optional[str] = None  # YYYY-MM-DD
    scheduled_hour: Optional[int] = None
    scheduled_minute: Optional[int] = None

    @field_validator("scheduled_hour", "scheduled_minute")
    @classmethod
    def non_negative(cls, v):
        if v is not None and v < 0:
            raise ValueError("must be non-negative")
        return v


class PostUpdate(PostBase):
    status: Optional[str] = None


class PostOut(BaseModel):
    id: int
    owner_id: int
    content: str
    status: str
    scheduled_at: datetime | None
    published_at: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True


class ReactionCreate(BaseModel):
    type: str
