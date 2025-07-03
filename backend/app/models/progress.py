from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base

class Progress(Base):
    __tablename__ = "progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    progress_percent = Column(Float, nullable=False)
    last_activity = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="progress_records")
    course = relationship("Course", back_populates="progress_records")
