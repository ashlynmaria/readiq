from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.course import Course
from core.database import get_db
from schemas.course import CourseCreate, CourseOut
from routes.auth import get_current_user
from models.user import User

router = APIRouter(prefix="/api/protected/courses", tags=["courses"])

@router.post("/", response_model=CourseOut)
async def create_course(
    data: CourseCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    course = Course(
        title=data.title,
        description=data.description,
        reading_level=data.reading_level,
        age_range=data.age_range,
        difficulty=data.difficulty,
        language=data.language,
        estimated_duration=data.estimated_duration,
        tags=data.tags,
    )
    db.add(course)
    await db.commit()
    await db.refresh(course)
    return course

@router.get("/", response_model=list[CourseOut])
async def list_courses(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Course))
    return result.scalars().all()

@router.put("/{course_id}", response_model=CourseOut)
async def edit_course(
    course_id: int,
    data: CourseCreate,  # you can reuse CourseCreate for editing
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")

    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    course.title = data.title
    course.description = data.description
    course.reading_level = data.reading_level
    course.age_range = data.age_range
    course.difficulty = data.difficulty
    course.language = data.language
    course.estimated_duration = data.estimated_duration
    course.tags = data.tags

    await db.commit()
    await db.refresh(course)
    return course


@router.delete("/{course_id}")
async def delete_course(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")

    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    await db.delete(course)
    await db.commit()
    return {"detail": "Course deleted successfully"}
