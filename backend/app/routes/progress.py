from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.progress import Progress
from models.user import User
from schemas.progress import ProgressCreate, ProgressUpdate, ProgressOut
from core.database import get_db
from routes.auth import get_current_user

router = APIRouter(prefix="/api/protected/progress", tags=["progress"])

@router.post("/", response_model=ProgressOut)
async def create_progress(
    data: ProgressCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
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
    progress.progress_percent = data.progress_percent
    await db.commit()
    await db.refresh(progress)
    return progress
