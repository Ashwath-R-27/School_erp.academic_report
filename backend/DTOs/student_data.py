from datetime import date
from typing import Optional

from fastapi import Form
from pydantic import BaseModel, Field


class SSLCStudentForm(BaseModel):
    """DTO for SSLC student details form submission."""

    name: str = Field(..., min_length=1, max_length=30)
    reg_no: int
    dob: date
    sec: str = Field(..., min_length=1, max_length=1)

    @classmethod
    def as_form(
        cls,
        name: str = Form(..., min_length=1, max_length=30),
        reg_no: int = Form(...),
        dob: date = Form(...),
        sec: str = Form(..., min_length=1, max_length=1),
    ) -> "SSLCStudentForm":
        return cls(name=name, reg_no=reg_no, dob=dob, sec=sec)


class HSCStudentForm(BaseModel):
    """DTO for HSC student details form submission."""

    name: str = Field(..., min_length=1, max_length=30)
    reg_no: int
    dob: date
    sec: str = Field(..., min_length=1, max_length=4)  # accommodates A1, G1 etc.
    grp: str = Field(..., min_length=1, max_length=6)

    @classmethod
    def as_form(
        cls,
        name: str = Form(..., min_length=1, max_length=30),
        reg_no: int = Form(...),
        dob: date = Form(...),
        sec: str = Form(..., min_length=1, max_length=4),
        grp: str = Form(..., min_length=1, max_length=6),
    ) -> "HSCStudentForm":
        return cls(name=name, reg_no=reg_no, dob=dob, sec=sec, grp=grp)


class StudentSubmitResponse(BaseModel):
    """Standard success response for student data submission endpoints."""

    message: str = "success"
    name: str
    reg_no: int

    model_config = {"from_attributes": True}
