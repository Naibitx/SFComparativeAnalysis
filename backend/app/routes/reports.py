from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/")
def get_reports():
    return {
        "reports": [
            {
                "id": 1,
                "run_id": "demo-run-1",
                "task": "Task A – Read Text File",
                "language": "Python",
                "date": datetime.now().isoformat(),
                "winner": "ChatGPT",
                "assistants": 2,
                "status": "completed",
            }
        ]
    }


@router.get("/{report_id}")
def get_report(report_id: str):
    return {
        "id": report_id,
        "message": "Single report endpoint working"
    }