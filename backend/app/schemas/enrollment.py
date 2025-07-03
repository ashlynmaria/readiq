from pydantic import BaseModel
from datetime import datetime

class EnrollmentCreate(BaseModel):
    student_id: int
    course_id: int

class EnrollmentOut(BaseModel):
    id: int
    student_id: int
    course_id: int
    assigned_by: int | None
    assigned_on: datetime   # ← allow datetime directly

    class Config:
        from_attributes = True
