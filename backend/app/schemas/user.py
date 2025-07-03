from pydantic import BaseModel, EmailStr  

class UserCreate(BaseModel):
    username: str
    password: str
    email: str

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    role: str
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdatePassword(BaseModel):
    new_password: str

class UserUpdate(BaseModel):
    username: str
    email: EmailStr

class UserUpdateRole(BaseModel):
    username: str
    role: str

class StudentOut(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True

class StudentUpdate(BaseModel):
    username: str
    email: EmailStr
