from pydantic import BaseModel, Field


class ExamResultSummaryDTO(BaseModel):
    appeared: int = Field(..., description="Total number of students who appeared")
    passed: int = Field(..., description="Number of students who passed")
    failed: int = Field(..., description="Number of students who failed")
    pass_percentage: float = Field(
        ..., description="Pass percentage rounded to two decimal places"
    )


class ResultsSummaryDTO(BaseModel):
    hsc: ExamResultSummaryDTO
    sslc: ExamResultSummaryDTO