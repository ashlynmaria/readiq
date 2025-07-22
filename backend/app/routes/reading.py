import os
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from routes.auth import get_current_user
from models.user import User

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter(prefix="/api/protected/reading", tags=["reading"])

@router.post("/upload")
async def upload_text_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    if file.content_type != "text/plain":
        raise HTTPException(status_code=400, detail="Only .txt files are supported for now")

    filename = f"{current_user.id}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    return {"detail": "Uploaded successfully", "filename": filename}


@router.get("/read/{filename}")
async def read_uploaded_file(
    filename: str,
    current_user: User = Depends(get_current_user)
):
    file_path = os.path.join(UPLOAD_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    return {"content": content}
