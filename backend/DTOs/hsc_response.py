from typing import Optional

from pydantic import BaseModel, Field


class TopperResponse(BaseModel):
    rank: int
    reg_no: int
    class_: str = Field(..., alias="class")  # Maps 'class_' to 'class' in JSON
    group: Optional[str]
    name: str
    lang: int
    eng: int
    sub1: int
    sub2: int
    sub3: int
    sub4: Optional[int]
    total: int
    cutoff: Optional[float]

    class Config:
        populate_by_name = True
