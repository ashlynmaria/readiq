from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.user import User
from core.database import get_db
from routes.auth import get_current_user
from schemas.user import UserOut, UserUpdate, UserUpdatePassword
from core.security import hash_password
from fastapi import status
from schemas.user import UserUpdateRole

router = APIRouter()


@router.get("/me", response_model=UserOut)
async def read_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/change-password")
async def change_password(
    data: UserUpdatePassword,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    current_user.hashed_password = hash_password(data.new_password)
    await db.commit()
    return {"detail": "Password changed successfully"}


@router.post("/update-profile", response_model=UserOut)
async def update_profile(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    current_user.username = data.username
    current_user.email = data.email
    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.delete("/delete-account")
async def delete_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await db.delete(current_user)
    await db.commit()
    return {"detail": "Account deleted successfully"}



@router.get("/users", response_model=list[UserOut])
async def list_all_users(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users

@router.get("/all-users", response_model=list[UserOut])
async def list_all_users(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admins only")

    result = await db.execute(select(User))
    users = result.scalars().all()
    return users

@router.post("/update-role", response_model=UserOut)
async def update_user_role(
    data: UserUpdateRole,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # only admins can do this
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")

    result = await db.execute(select(User).where(User.username == data.username))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = data.new_role
    await db.commit()
    await db.refresh(user)
    return user

@router.post("/deactivate-user/{user_id}")
async def deactivate_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False
    await db.commit()
    return {"detail": f"User {user.username} deactivated"}

@router.get("/all-users", response_model=list[UserOut])
async def list_all_users(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    result = await db.execute(select(User).where(User.is_active == True))
    users = result.scalars().all()
    return users

@router.post("/reactivate-user/{user_id}")
async def reactivate_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = True
    await db.commit()
    return {"detail": f"User {user.username} reactivated"}

@router.get("/me")
async def get_my_profile(current_user=Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "role": current_user.role,
        "email": current_user.email,
        "verified": current_user.verified,
    }@router.get("/me")

async def get_my_profile(current_user=Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "role": current_user.role,
        "email": current_user.email,
        "verified": current_user.verified,
    }