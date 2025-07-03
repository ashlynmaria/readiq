from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from core.database import Base

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    reading_level = Column(String, nullable=True)  # e.g. Beginner, Intermediate
    age_range = Column(String, nullable=True)      # e.g. "7-10"
    difficulty = Column(Integer, nullable=True)    # 1–5
    language = Column(String, nullable=True)       # e.g. "English"
    estimated_duration = Column(Integer, nullable=True)  # in minutes
    tags = Column(String, nullable=True)           # comma-separated tags

    progress_records = relationship("Progress", back_populates="course", cascade="all, delete")
