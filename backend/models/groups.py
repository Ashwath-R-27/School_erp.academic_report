from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Column, String
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .hsc import HSC


class Group(SQLModel, table=True):
    __tablename__ = "groups"

    group_id: int = Field(primary_key=True)
    code: str = Field(sa_column=Column("code", String(20), unique=True, nullable=False))
    name: str
    subject1: Optional[str] = None
    subject2: Optional[str] = None
    subject3: Optional[str] = None
    subject4: Optional[str] = None

    hsc_students: List["HSC"] = Relationship(back_populates="group")