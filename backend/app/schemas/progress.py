from pydantic import BaseModel
from datetime import datetime

class ProgressCreate(BaseModel):
    course_id: int
    progress_percent: float

class ProgressUpdate(BaseModel):
    progress_percent: float

class ProgressOut(BaseModel):
    id: int
    user_id: int
    course_id: int
    progress_percent: float
    last_activity: datetime

    class Config:
        from_attributes = True
