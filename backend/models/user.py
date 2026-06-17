import uuid
from typing import List, Optional

from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(sa_column=Column(UUID(as_uuid=True), primary_key=True))
    name: Optional[str] = None
    password: Optional[str] = None
    email: Optional[str] = None
    phno: Optional[int] = Field(default=None, sa_column=Column("phno", Integer))
    class_: Optional[List[str]] = Field(
        default=None, sa_column=Column("class", ARRAY(String))
    )
    subject: Optional[List[str]] = Field(
        default=None, sa_column=Column("subject", ARRAY(String))
    )