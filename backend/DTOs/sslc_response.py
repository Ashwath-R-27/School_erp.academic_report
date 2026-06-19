from typing import List, Optional

from pydantic import BaseModel, Field


class SSLCFailureResponse(BaseModel):
    reg_no: int
    class_: str = Field(..., alias="class")
    name: str
    tamil: Optional[int] = None
    english: Optional[int] = None
    maths: Optional[int] = None
    science: Optional[int] = None
    social: Optional[int] = None
    total: Optional[int] = None

    model_config = {"populate_by_name": True, "from_attributes": True}


class SSLCTopperResponse(BaseModel):
    rank: int
    reg_no: int
    class_: str = Field(..., alias="class")  # Maps 'class_' to 'class' in JSON
    name: str
    tamil: Optional[int] = None
    english: Optional[int] = None
    maths: Optional[int] = None
    science: Optional[int] = None
    social: Optional[int] = None
    total: Optional[int] = None

    class Config:
        populate_by_name = True


class SSLCClasswiseResponseDTO(BaseModel):
    datas: List[SSLCTopperResponse]
