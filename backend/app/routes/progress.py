from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.progress import Progress
from models.user import User
from schemas.progress import ProgressCreate, ProgressUpdate, ProgressOut
from core.database import get_db
from routes.auth import get_current_user
from models.enrollment import Enrollment

router = APIRouter(prefix="/api/protected/progress", tags=["progress"])

@router.post("/", response_model=ProgressOut)
async def create_progress(
    data: ProgressCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Enrollment).where(
            Enrollment.student_id == current_user.id,
            Enrollment.course_id == data.course_id
        )
    )
    enrolled = result.scalar_one_or_none()
    if not enrolled:
        raise HTTPException(status_code=400, detail="Student not enrolled in this course")

    new_progress = Progress(
        user_id=current_user.id,
        course_id=data.course_id,
        progress_percent=data.progress_percent
    )
    db.add(new_progress)
    await db.commit()
    await db.refresh(new_progress)
    return new_progress

@router.get("/", response_model=list[ProgressOut])
async def list_progress(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Progress).where(Progress.user_id == current_user.id))
    return result.scalars().all()

@router.put("/{progress_id}", response_model=ProgressOut)
async def update_progress(
    progress_id: int,
    data: ProgressUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Progress).where(
            Progress.id == progress_id,
            Progress.user_id == current_user.id
        )
    )
    progress = result.scalar_one_or_none()
    if not progress:
        raise HTTPException(status_code=404, detail="Progress record not found")
    
    # check enrollment
    enrollment_check = await db.execute(
        select(Enrollment).where(
            Enrollment.student_id == current_user.id,
            Enrollment.course_id == progress.course_id
        )
    )
    enrolled = enrollment_check.scalar_one_or_none()
    if not enrolled:
        raise HTTPException(status_code=400, detail="Student not enrolled in this course")
    
    progress.progress_percent = data.progress_percent
    await db.commit()
    await db.refresh(progress)
    return progress

@router.get("/course/{course_id}", response_model=list[ProgressOut])
async def get_progress_for_course(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # check enrollment
    result = await db.execute(
        select(Enrollment).where(
            Enrollment.student_id == current_user.id,
            Enrollment.course_id == course_id
        )
    )
    enrolled = result.scalar_one_or_none()
    if not enrolled:
        raise HTTPException(status_code=400, detail="Not enrolled in this course")

    result = await db.execute(
        select(Progress).where(
            Progress.user_id == current_user.id,
            Progress.course_id == course_id
        )
    )
    return result.scalars().all()
