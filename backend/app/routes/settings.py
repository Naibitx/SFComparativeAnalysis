from fastapi import APIRouter
from app.config import get_settings

router = APIRouter()


@router.get("/config")
def get_config():
    settings = get_settings()
    return {
        "app_name": settings.app_name,
        "database_url": settings.database_url,
        "workspace_dir": settings.workspace_dir,
        "reports_dir": settings.reports_dir,
        "debug": settings.debug,
    }


@router.put("/config")
def update_config(payload: dict):
    return {
        "message": "Config received. Permanent .env editing is not enabled through the UI yet.",
        "received": payload,
    }


@router.get("/logs")
def get_logs():
    return {
        "logs": [
            "Backend is running",
            "SQLite database is connected",
            "Evaluation routes are active",
        ]
    }