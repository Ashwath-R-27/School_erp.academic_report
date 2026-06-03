from typing import Optional

from sqlalchemy import Column, String
from sqlmodel import Field, SQLModel


class SSLC(SQLModel, table=True):
    __tablename__ = "sslc"

    reg_no: int = Field(primary_key=True)
    class_: str = Field(sa_column=Column("class", String(1), nullable=False))
    first_name: Optional[str] = Field(default=None, max_length=15)
    last_name: Optional[str] = Field(default=None, max_length=15)
    tamil: Optional[int] = None
    english: Optional[int] = None
    maths: Optional[int] = None
    science: Optional[int] = None
    social: Optional[int] = None

    # Generated column from DB side is marked as completely optional/read-only during creation
    total: Optional[int] = Field(
        default=None,
        sa_column_kwargs={
            "schema": "GENERATED ALWAYS AS (tamil + english + maths + science + social) STORED"
        },
    )
