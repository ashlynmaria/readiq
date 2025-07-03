from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from schemas.user import UserCreate, UserOut, UserLogin
from models.user import User
from core.database import get_db
from core.security import hash_password, verify_password, create_access_token
from core.config import settings
from jose import jwt, JWTError
from services.email_utils import send_verification_email

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# Helper to create email verification token
def create_email_token(email: str):
    return jwt.encode({"sub": email}, settings.JWT_SECRET, algorithm="HS256")


@router.post("/register", response_model=UserOut)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user_in.email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        role="student",
        is_active=True,
        verified=False,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    email_token = create_email_token(user.email)
    await send_verification_email(user.email, email_token)

    return user


@router.get("/verify-email")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=400, detail="Invalid token")
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user.verified = True
        await db.commit()
        return {"detail": "Email verified successfully"}
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired token")


@router.post("/login")
async def login(user_in: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user_in.email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="This user account is deactivated")
    if not user.verified:
        raise HTTPException(status_code=401, detail="Email not verified")

    token = create_access_token({"sub": user.email, "role": user.role, "id": user.id})
    return {"access_token": token, "token_type": "bearer"}


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        email: str = payload.get("sub")   # sub is email
        role: str = payload.get("role")
        if email is None or role is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        if not user.is_active:
            raise HTTPException(status_code=403, detail="This user account is deactivated")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
