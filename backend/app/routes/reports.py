from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.Models.evaluation_run import EvaluationRun
from app.Models.coding_task import CodingTask

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
            "task": first.coding_task.title,
            "language": first.language.name if first.language else "Python",
            "date": first.created_at.isoformat() if first.created_at else "",
            "winner": winner.assistant.name,
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
                "assistant": run.assistant.name,
                "score": run.overall_score,
                "success": run.execution_success,
                "time_ms": run.execution_time_ms,
            }
            for run in runs
        ],
    }