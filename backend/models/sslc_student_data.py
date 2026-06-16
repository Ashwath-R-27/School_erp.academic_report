from datetime import date
from typing import Optional

from sqlalchemy import Column, String
from sqlmodel import Field, SQLModel


class SSLCStudentData(SQLModel, table=True):
    __tablename__ = "sslc_student_data"

    reg_no: int = Field(primary_key=True)
    name: Optional[str] = Field(default=None, max_length=30)
    class_: Optional[str] = Field(
        default=None, sa_column=Column("class", String(1))
    )
    dob: Optional[date] = None
