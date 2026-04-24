from fastapi import APIRouter

router = APIRouter()

CONFIG = {
    "framework": "AI assistant evaluation system",
    "execution_timeout": "10",
    "workspace_dir": "./workspace",
    "reports_dir": "./reports/generated",
}

@router.get("/config")
def get_config():
    return CONFIG


@router.put("/config")
def update_config(payload: dict):
    CONFIG.update(payload)
    return CONFIG


@router.get("/logs")
def get_logs():
    return {
        "logs": [
            "Backend started successfully",
            "Admin settings endpoint working",
            "Logs endpoint working",
        ]
    }


@router.get("/")
def settings():
    return CONFIG