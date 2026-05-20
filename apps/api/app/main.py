from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import auth, contributions, dashboard, members, reports
from app.core.config import get_settings

from app.db.session import Base, engine
import app.models  # noqa: F401

settings = get_settings()

app = FastAPI(title="KOSH Saving API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:3000",
    "https://kosh-web-chi.vercel.app",
    "https://sachinchakradhar.com.np",
    "https://www.sachinchakradhar.com.np",
],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    
)

if settings.auto_create_tables:
    Base.metadata.create_all(bind=engine)

Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

app.include_router(auth.router, prefix="/api")
app.include_router(members.router, prefix="/api")
app.include_router(contributions.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(reports.router, prefix="/api")


@app.get("/health")
def health_check():
    return {"status": "ok", "app": settings.app_name}
