from datetime import date, datetime
from uuid import UUID
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlmodel import Field, SQLModel, func, text
from typing import Optional


# Base class that includes special encoders for Enums and other data types.
class SchemaBase(SQLModel):
    def jsond(model: SQLModel):
        return jsonable_encoder(model.dict(exclude_unset=True))

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
            date: lambda dt: dt.strftime("%Y-%m-%d"),
        }
        use_enum_values = True


class ModelBase(SchemaBase):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(
        sa_column_kwargs={
            "server_default": text("CURRENT_TIMESTAMP"),
        },
        nullable=False,
    )
    updated_at: Optional[datetime] = Field(
        sa_column_kwargs={
            "server_default": text("CURRENT_TIMESTAMP"),
            "onupdate": func.now(),
        },
        nullable=False,
    )


class TokenPayload(BaseModel):
    sub: Optional[UUID] = None
