from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from core.database import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)        
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="student")
    is_active = Column(Boolean, default=True)
    verified = Column(Boolean, default=False)
    parent_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    progress_records = relationship(
        "Progress", back_populates="user", cascade="all, delete"
    )

    students = relationship(
        "User",
        back_populates="parent",
        cascade="all, delete",
        foreign_keys="[User.parent_id]"
    )

    parent = relationship(
        "User",
        back_populates="students",
        remote_side="User.id"
    )


