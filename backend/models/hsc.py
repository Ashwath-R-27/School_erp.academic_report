from typing import Optional

from sqlalchemy import Column, String
from sqlmodel import Field, SQLModel


class HSC(SQLModel, table=True):
    __tablename__ = "hsc"

    reg_no: int = Field(primary_key=True)
    class_: str = Field(sa_column=Column("class", String, nullable=False))
    name: str
    group_name: Optional[str] = None
    lang: int
    eng: int
    sn1: str
    sn2: str
    sn3: str
    sn4: Optional[str] = None
    sm1: int
    sm2: int
    sm3: int
    sm4: Optional[int] = None

    # Generated columns from DB side
    total: Optional[int] = Field(default=None)
    cut_off: Optional[float] = Field(default=None)
