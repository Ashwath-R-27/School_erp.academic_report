from typing import Optional

from sqlalchemy import Column, FetchedValue, String
from sqlmodel import Field, SQLModel


class SSLC(SQLModel, table=True):
    __tablename__ = "sslc"

    reg_no: int = Field(primary_key=True)
    class_: str = Field(sa_column=Column("class", String(1), nullable=False))
    name: Optional[str] = Field(default=None, max_length=30)
    tamil: Optional[int] = None
    english: Optional[int] = None
    maths: Optional[int] = None
    science: Optional[int] = None
    social: Optional[int] = None

    # Tells SQLModel the DB handles this value automatically on insert/update
    total: Optional[int] = Field(
        default=None, sa_column_kwargs={"server_default": FetchedValue()}
    )
