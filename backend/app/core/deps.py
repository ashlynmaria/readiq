from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        email: str = payload.get("sub")    
        role: str = payload.get("role")
        if email is None or role is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"email": email, "role": role}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
