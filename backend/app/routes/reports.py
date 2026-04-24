from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.Models.evaluation_run import EvaluationRun

router = APIRouter()


@router.get("/")
def get_reports(db: Session = Depends(get_db)):
    runs = db.query(EvaluationRun).order_by(EvaluationRun.created_at.desc()).all()

    grouped = {}
    for run in runs:
        grouped.setdefault(run.run_id, []).append(run)

    reports = []

    for run_id, group in grouped.items():
        first = group[0]
        winner = max(group, key=lambda r: r.overall_score or 0)

        reports.append({
            "id": run_id,
            "run_id": run_id,
            "task": first.coding_task.name if first.coding_task else "Unknown Task",
            "task_id": first.coding_task.task_code if first.coding_task else "",
            "language": first.language.name if first.language else "Python",
            "date": first.created_at.isoformat() if first.created_at else "",
            "winner": winner.assistant.name if winner.assistant else "Unknown",
            "assistants": len(group),
            "status": "completed",
        })

    return {"reports": reports}


@router.get("/{run_id}")
def get_report(run_id: str, db: Session = Depends(get_db)):
    runs = db.query(EvaluationRun).filter(EvaluationRun.run_id == run_id).all()

    return {
        "run_id": run_id,
        "results": [
            {
                "assistant": run.assistant.name if run.assistant else "Unknown",
                "task": run.coding_task.name if run.coding_task else "Unknown Task",
                "language": run.language.name if run.language else "Python",
                "score": run.overall_score,
                "success": run.execution_success,
                "time_ms": run.execution_time_ms,
                "output": run.execution_output,
                "error": run.execution_error,
            }
            for run in runs
        ],
    }