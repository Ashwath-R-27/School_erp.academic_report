from datetime import date
from typing import Optional

from sqlalchemy import Column, String
from sqlmodel import Field, SQLModel


class HSCStudentData(SQLModel, table=True):
    __tablename__ = "hsc_student_data"

    reg_no: int = Field(primary_key=True)
    name: Optional[str] = Field(default=None, max_length=30)
    class_: Optional[str] = Field(
        default=None, sa_column=Column("class", String)
    )
    dob: Optional[date] = None
    group_code: Optional[str] = Field(
        default=None, sa_column=Column("group_code", String(6))
    )
