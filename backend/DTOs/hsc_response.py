from typing import List, Optional

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


class SubjectFirstMarkResponse(BaseModel):
    name: str
    mark: int
    count: int


class StudentGroupwiseDTO(BaseModel):
    rank: int
    reg_no: int
    class_: str = Field(..., alias="class")
    group: str
    name: str
    lang: int
    eng: int
    sub1: int
    sub2: int
    sub3: int
    sub4: Optional[int] = None
    total: int
    cutoff: Optional[float] = Field(None, alias="cutoff")

    # Ensures compatibility with both direct assignment and dictionary matching
    model_config = {"populate_by_name": True, "from_attributes": True}


class GroupwiseResponseDTO(BaseModel):
    datas: List[StudentGroupwiseDTO]
