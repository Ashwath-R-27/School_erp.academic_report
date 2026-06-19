from typing import Any, List, Union

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel

JsonData = Union[List[Any], dict[str, Any]]


class JsonDump(SQLModel, table=True):
    __tablename__ = "json_dumps"

    key: str = Field(primary_key=True, max_length=100)
    data: JsonData = Field(sa_column=Column(JSONB, nullable=False))