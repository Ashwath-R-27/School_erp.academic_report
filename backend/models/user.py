from typing import Optional

from sqlalchemy import Column, FetchedValue, String
from sqlmodel import Field, SQLModel


class SSLC(SQLModel, table=True):
    __tablename__ = "user"

    id: int = Field(primary_key=True)
