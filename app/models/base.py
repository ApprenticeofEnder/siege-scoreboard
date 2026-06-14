from datetime import datetime

from sqlmodel import Column, DateTime, Field, SQLModel, func


class BaseDbModel(SQLModel):
    created_at: datetime | None = Field(
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), nullable=True
        )
    )
    updated_at: datetime | None = Field(
        sa_column=Column(
            DateTime(timezone=True),
            onupdate=func.now(),
            nullable=True,
        )
    )


class BaseDbModelWithId(BaseDbModel):
    id: int | None = Field(default=None, primary_key=True)
