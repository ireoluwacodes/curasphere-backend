from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel
from src.api.base_model import TimestampMixin


class User(TimestampMixin, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    username: str
    email: str
    password: str
    otp: Optional[str] = Field(default=None, nullable=True)
    otp_expiry: Optional[datetime] = Field(default=None, nullable=True)
