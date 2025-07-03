from pydantic import BaseModel

class CourseCreate(BaseModel):
    title: str
    description: str | None = None
    reading_level: str | None = None
    age_range: str | None = None
    difficulty: int | None = None
    language: str | None = None
    estimated_duration: int | None = None
    tags: str | None = None

class CourseOut(CourseCreate):
    id: int

    class Config:
        from_attributes = True
