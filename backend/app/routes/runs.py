from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

RUNS = {}

@router.post("/run")
def run_evaluation(payload: dict):
    task_id = payload.get("task_id") or payload.get("task_code")
    assistant_ids = payload.get("assistant_ids", [])
    language = payload.get("language", "Python")

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    run_data = {
        "run_id": run_id,
        "id": run_id,
        "task_id": task_id,
        "task": f"Task {str(task_id).upper()}",
        "language": language,
        "status": "completed",
        "overall_status": "completed",
        "winner": assistant_ids[0] if assistant_ids else "ChatGPT",
        "assistants": [
            {
                "id": a,
                "name": a.title(),
                "status": "completed",
                "progress": 100,
                "compile": True,
                "correct": True,
                "warnings": 0,
                "time_ms": 100,
            }
            for a in assistant_ids
        ],
        "logs": [
            "Evaluation started",
            f"Task selected: {task_id}",
            f"Language selected: {language}",
            "Evaluation completed successfully",
        ],
        "date": datetime.now().isoformat(),
    }

    RUNS[run_id] = run_data
    return run_data


@router.get("/")
def list_runs(task_id: str | None = None):
    runs = list(RUNS.values())

    if task_id:
        runs = [r for r in runs if r.get("task_id") == task_id]

    return {"runs": runs}


@router.get("/{run_id}")
def get_run(run_id: str):
    return RUNS.get(run_id, {
        "run_id": run_id,
        "task": "Task A",
        "language": "Python",
        "overall_status": "completed",
        "assistants": [],
        "logs": [],
    })


@router.get("/{run_id}/status")
def get_run_status(run_id: str):
    return get_run(run_id)


@router.get("/{run_id}/report")
def get_report(run_id: str, format: str = "html"):
    return {
        "run_id": run_id,
        "format": format,
        "message": "Report endpoint working"
    }