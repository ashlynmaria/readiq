from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings

from routes import auth, protected, progress, students, courses, enrollment

app = FastAPI(title="ReadIQ API")

# Debug print to confirm .env loaded
# print("✅ BREVO login loaded from env:", settings.BREVO_LOGIN)
print("✅ Gmail loaded from env:", settings.EMAIL_FROM)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# register routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(protected.router, prefix="/api/protected", tags=["protected"])
app.include_router(progress.router)
app.include_router(students.router)
app.include_router(courses.router)
app.include_router(enrollment.router)

@app.get("/")
async def root():
    return {"message": "ReadIQ API is working ✅"}
