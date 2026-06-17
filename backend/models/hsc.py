from typing import TYPE_CHECKING, Optional

from sqlalchemy import Column, FetchedValue, String
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .groups import Group


class HSC(SQLModel, table=True):
    __tablename__ = "hsc"

    reg_no: int = Field(primary_key=True)
    class_: Optional[str] = Field(default=None, sa_column=Column("class", String))
    name: Optional[str] = None

    group_id: Optional[int] = Field(default=None, foreign_key="groups.group_id")
    group_code: Optional[str] = Field(
        default=None, sa_column=Column("group_code", String(20))
    )

    lang_name: Optional[str] = None
    lang: Optional[int] = None
    eng: Optional[int] = None

    mark_1: Optional[int] = None
    mark_2: Optional[int] = None
    mark_3: Optional[int] = None
    mark_4: Optional[int] = None

    total: Optional[int] = Field(
        default=None, sa_column_kwargs={"server_default": FetchedValue()}
    )
    cut_off: Optional[float] = Field(
        default=None, sa_column_kwargs={"server_default": FetchedValue()}
    )

    group: Optional["Group"] = Relationship(back_populates="hsc_students")