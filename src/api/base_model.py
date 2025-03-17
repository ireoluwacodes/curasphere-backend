from datetime import datetime
from pydantic import BaseModel
from sqlmodel import Field
from typing import Optional


class TimestampMixin:
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TokenPayload(BaseModel):
    sub: Optional[int] = None
