from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from core.database import get_db
from models.enrollment import Enrollment
from models.course import Course
from models.user import User
from schemas.enrollment import EnrollmentCreate, EnrollmentOut
from routes.auth import get_current_user

router = APIRouter(prefix="/api/protected/enrollments", tags=["enrollments"])

@router.post("/", response_model=EnrollmentOut)
async def enroll_student(
    data: EnrollmentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role not in ["parent", "teacher", "admin"]:
        raise HTTPException(status_code=403, detail="Not authorized to enroll")

    # confirm student exists
    result = await db.execute(
        select(User).where(User.id == data.student_id, User.role == "student")
    )
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # confirm course exists
    result = await db.execute(select(Course).where(Course.id == data.course_id))
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # check if already enrolled
    result = await db.execute(
        select(Enrollment).where(
            Enrollment.student_id == data.student_id,
            Enrollment.course_id == data.course_id,
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Student already enrolled")

    enrollment = Enrollment(
        student_id=data.student_id,
        course_id=data.course_id,
        assigned_by=current_user.id,
    )
    db.add(enrollment)
    await db.commit()
    await db.refresh(enrollment)
    return enrollment


@router.get("/{student_id}", response_model=list[EnrollmentOut])
async def list_enrollments(
    student_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # allow admin to view any, parents/teachers only their students
    if current_user.role in ["parent", "teacher"]:
        student_check = await db.execute(
            select(User).where(User.id == student_id, User.parent_id == current_user.id)
        )
        student = student_check.scalar_one_or_none()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found or not yours.")
    elif current_user.role == "admin":
        pass
    else:
        raise HTTPException(status_code=403, detail="Not authorized")

    result = await db.execute(
        select(Enrollment).where(Enrollment.student_id == student_id)
    )
    return result.scalars().all()


@router.delete("/{enrollment_id}")
async def unenroll_student(
    enrollment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role not in ["parent", "teacher", "admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    result = await db.execute(select(Enrollment).where(Enrollment.id == enrollment_id))
    enrollment = result.scalar_one_or_none()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")

    # extra: parents/teachers can only unenroll their students
    if current_user.role in ["parent", "teacher"]:
        student_check = await db.execute(
            select(User).where(User.id == enrollment.student_id, User.parent_id == current_user.id)
        )
        student = student_check.scalar_one_or_none()
        if not student:
            raise HTTPException(status_code=403, detail="Not authorized to remove this enrollment")

    await db.delete(enrollment)
    await db.commit()
    return {"detail": "Unenrolled successfully"}
