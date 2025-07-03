from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.user import User
from core.database import get_db
from routes.auth import get_current_user
from schemas.user import UserCreate, StudentOut
from core.security import hash_password
from schemas.user import StudentUpdate
from models.progress import Progress
from schemas.progress import ProgressOut

router = APIRouter(prefix="/api/protected/students", tags=["students"])


@router.post("/create", response_model=StudentOut)
async def create_student(
    data: UserCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role not in ["parent", "teacher", "admin"]:
        raise HTTPException(status_code=403, detail="Not authorized to create students")

    # check email not reused
    result = await db.execute(select(User).where(User.email == data.email))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    new_student = User(
        username=data.username,
        email=data.email,
        hashed_password=hash_password(data.password),
        role="student",
        is_active=True,
        verified=True,  # parent-created accounts are auto-verified
        parent_id=current_user.id
    )
    db.add(new_student)
    await db.commit()
    await db.refresh(new_student)
    return new_student


@router.get("/my-students", response_model=list[StudentOut])
async def list_my_students(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role not in ["parent", "teacher", "admin"]:
        raise HTTPException(status_code=403, detail="Not authorized to view students")

    result = await db.execute(select(User).where(User.parent_id == current_user.id))
    return result.scalars().all()

@router.put("/edit/{student_id}", response_model=StudentOut)
async def edit_student(
    student_id: int,
    data: StudentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # make sure this student belongs to this parent/teacher
    result = await db.execute(
        select(User).where(User.id == student_id, User.parent_id == current_user.id)
    )
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found or not yours.")

    # update fields
    student.username = data.username
    student.email = data.email

    await db.commit()
    await db.refresh(student)
    return student

@router.get("/{student_id}/progress", response_model=list[ProgressOut])
async def get_student_progress(
    student_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role in ["parent", "teacher"]:
        # parents/teachers: only their own students
        result = await db.execute(
            select(User).where(User.id == student_id, User.parent_id == current_user.id)
        )
    elif current_user.role == "admin":
        # admin: can see any student
        result = await db.execute(
            select(User).where(User.id == student_id, User.role == "student")
        )
    else:
        raise HTTPException(status_code=403, detail="Not authorized")

    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found or not yours.")

    progress_result = await db.execute(
        select(Progress).where(Progress.user_id == student_id)
    )
    progress = progress_result.scalars().all()
    return progress
    
@router.post("/deactivate/{student_id}")
async def deactivate_student(
    student_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).where(User.id == student_id, User.parent_id == current_user.id)
    )
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found or not yours.")

    student.is_active = False
    await db.commit()
    return {"detail": f"Student {student.username} deactivated."}


@router.post("/reactivate/{student_id}")
async def reactivate_student(
    student_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).where(User.id == student_id, User.parent_id == current_user.id)
    )
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found or not yours.")

    student.is_active = True
    await db.commit()
    return {"detail": f"Student {student.username} reactivated."}
