from datetime import datetime
import ast
import subprocess
import sys
import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.Models.assistant import Assistant
from app.Models.coding_task import CodingTask
from app.Models.language import Language
from app.Models.evaluation_run import EvaluationRun, RunStatus
from app.Models.security_finding import SecurityFinding, FindingSeverity
from app.services.prompt_builder import build_prompt
from app.services.readability_engine import ReadabilityEngine
from app.config import get_settings

router = APIRouter()
readability_engine = ReadabilityEngine()


TASK_NAMES = {
    "a": "Task A – Read Text File",
    "b": "Task B – Read JSON with Threads",
    "c": "Task C – Write Text File",
    "d": "Task D – Write JSON with Threads",
    "e": "Task E – Create ZIP File",
    "f": "Task F – MySQL Query",
    "g": "Task G – MongoDB Query",
    "h": "Task H – Authentication",
}

ASSISTANT_NAMES = {
    "copilot": "GitHub Copilot",
    "chatgpt": "ChatGPT",
    "gemini": "Google Gemini",
    "claude": "Anthropic Claude",
    "grok": "Grok",
}


def get_or_create_assistant(db: Session, assistant_key: str) -> Assistant:
    name = ASSISTANT_NAMES.get(assistant_key, assistant_key.title())
    assistant = db.query(Assistant).filter(Assistant.name == name).first()

    if assistant:
        return assistant

    assistant = Assistant(
        name=name,
        provider=name,
        model_version="local-evaluation",
        description="Stored assistant record for evaluation results.",
        is_active=True,
    )
    db.add(assistant)
    db.commit()
    db.refresh(assistant)
    return assistant


def get_or_create_language(db: Session, language_name: str) -> Language:
    language = db.query(Language).filter(Language.name == language_name).first()

    if language:
        return language

    language = Language(name=language_name)
    db.add(language)
    db.commit()
    db.refresh(language)
    return language


def get_or_create_task(db: Session, task_code: str) -> CodingTask:
    task = db.query(CodingTask).filter(CodingTask.task_code == task_code).first()

    if task:
        return task

    task = CodingTask(
        task_code=task_code,
        title=TASK_NAMES.get(task_code, f"Task {task_code.upper()}"),
        description=build_prompt(task_code),
        prompt_text=build_prompt(task_code),
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def sample_generated_code(task_code: str, assistant_name: str) -> str:
    """
    This gives the backend real code to evaluate and store.
    Later, replace this with your actual API assistant.generate_code() calls.
    """
    header = f"# Generated for {assistant_name} - Task {task_code.upper()}\n"

    code_by_task = {
        "a": """
from pathlib import Path

def read_text_file(path: str) -> str:
    \"\"\"Read and return the contents of a text file.\"\"\"
    return Path(path).read_text(encoding="utf-8")

if __name__ == "__main__":
    print("Ready to read a text file.")
""",
        "b": """
import json
import threading
from pathlib import Path

def read_json_threaded(path: str) -> dict:
    \"\"\"Read a JSON file using a worker thread.\"\"\"
    result = {}

    def worker():
        result.update(json.loads(Path(path).read_text(encoding="utf-8")))

    thread = threading.Thread(target=worker)
    thread.start()
    thread.join()
    return result
""",
        "c": """
from pathlib import Path

def write_text_file(path: str, content: str) -> None:
    \"\"\"Write text content to a file.\"\"\"
    Path(path).write_text(content, encoding="utf-8")
""",
        "d": """
import json
import threading
from pathlib import Path

def write_json_threaded(path: str, data: dict) -> None:
    \"\"\"Write JSON data using a worker thread.\"\"\"
    def worker():
        Path(path).write_text(json.dumps(data, indent=2), encoding="utf-8")

    thread = threading.Thread(target=worker)
    thread.start()
    thread.join()
""",
        "e": """
import zipfile
from pathlib import Path

def create_zip(input_file: str, zip_file: str) -> None:
    \"\"\"Create a zip archive containing one input file.\"\"\"
    with zipfile.ZipFile(zip_file, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.write(input_file, arcname=Path(input_file).name)
""",
        "f": """
import mysql.connector

def get_sample_record(host: str, user: str, password: str, database: str):
    \"\"\"Connect to MySQL and retrieve one sample record.\"\"\"
    connection = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database,
    )
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM sample LIMIT 1")
    row = cursor.fetchone()
    cursor.close()
    connection.close()
    return row
""",
        "g": """
from pymongo import MongoClient

def get_sample_document(uri: str, database: str, collection: str):
    \"\"\"Connect to MongoDB and retrieve one sample document.\"\"\"
    client = MongoClient(uri)
    document = client[database][collection].find_one()
    client.close()
    return document
""",
        "h": """
import hashlib
import secrets

def hash_password(password: str) -> tuple[str, str]:
    \"\"\"Hash a password with a random salt.\"\"\"
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((salt + password).encode()).hexdigest()
    return salt, password_hash

def verify_password(password: str, salt: str, password_hash: str) -> bool:
    \"\"\"Verify a password against a stored salted hash.\"\"\"
    return hashlib.sha256((salt + password).encode()).hexdigest() == password_hash
""",
    }

    return header + code_by_task.get(task_code, "print('Unknown task')\n")


def evaluate_code(code: str, assistant_name: str, task_code: str) -> dict:
    syntax_success = True
    syntax_error = None

    try:
        ast.parse(code)
    except SyntaxError as exc:
        syntax_success = False
        syntax_error = str(exc)

    runtime_success = False
    runtime_error = None
    stdout = ""
    execution_time_ms = None

    if syntax_success:
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as temp:
            temp.write(code)
            temp_path = temp.name

        started = datetime.now()

        try:
            completed = subprocess.run(
                [sys.executable, temp_path],
                capture_output=True,
                text=True,
                timeout=10,
            )
            ended = datetime.now()
            execution_time_ms = round((ended - started).total_seconds() * 1000, 2)
            stdout = completed.stdout
            runtime_success = completed.returncode == 0
            runtime_error = completed.stderr if completed.returncode != 0 else None
        except Exception as exc:
            runtime_error = str(exc)

        Path(temp_path).unlink(missing_ok=True)

    readability = readability_engine.analyse(code)
    readability_score = readability.get("score") or 0

    warnings = 0
    findings = []

    if "eval(" in code or "exec(" in code:
        warnings += 1
        findings.append({
            "category": "Unsafe Execution",
            "severity": "high",
            "title": "Unsafe dynamic execution",
            "description": "Code contains eval() or exec().",
            "recommendation": "Avoid dynamic execution unless absolutely necessary.",
        })

    if "shell=True" in code:
        warnings += 1
        findings.append({
            "category": "Command Injection",
            "severity": "high",
            "title": "shell=True detected",
            "description": "Subprocess shell execution can be dangerous.",
            "recommendation": "Use argument lists and avoid shell=True.",
        })

    syntax_score = 100 if syntax_success else 0
    runtime_score = 100 if runtime_success else 0
    security_score = max(0, 100 - warnings * 25)

    overall_score = round(
        syntax_score * 0.30 +
        runtime_score * 0.25 +
        readability_score * 0.25 +
        security_score * 0.20,
        2,
    )

    return {
        "syntax_success": syntax_success,
        "syntax_error": syntax_error,
        "runtime_success": runtime_success,
        "runtime_error": runtime_error,
        "stdout": stdout,
        "execution_time_ms": execution_time_ms,
        "readability_score": readability_score,
        "security_warnings": warnings,
        "security_findings": findings,
        "overall_score": overall_score,
    }


def serialize_run_group(runs: list[EvaluationRun]) -> dict:
    if not runs:
        raise HTTPException(status_code=404, detail="Run not found")

    first = runs[0]
    assistants = []

    for run in runs:
        findings_count = len(run.security_findings or [])

        assistants.append({
            "id": run.assistant.name.lower().replace(" ", "_"),
            "name": run.assistant.name,
            "status": run.status.value if hasattr(run.status, "value") else str(run.status),
            "progress": 100,
            "compile": run.execution_error is None,
            "correct": run.execution_success,
            "warnings": findings_count,
            "time_ms": run.execution_time_ms,
            "memory_mb": None,
            "readability": None,
            "security": findings_count,
            "score": round((run.overall_score or 0) / 100, 2),
            "code": run.generated_code or "",
            "output": run.execution_output or "",
            "error": run.execution_error,
        })

    winner_run = max(runs, key=lambda r: r.overall_score or 0)
    winner_score = round((winner_run.overall_score or 0) / 100, 2)

    return {
        "run_id": first.run_id,
        "id": first.run_id,
        "task": first.coding_task.title,
        "task_id": first.coding_task.task_code,
        "language": first.language.name if first.language else "Python",
        "overall_status": "completed",
        "status": "completed",
        "winner": winner_run.assistant.name,
        "winner_score": winner_score,
        "winner_justification": (
            f"{winner_run.assistant.name} had the highest saved overall score "
            f"for this run: {winner_run.overall_score or 0}/100."
        ),
        "assistants": assistants,
        "logs": [
            f"Evaluation completed for {first.coding_task.title}",
            f"{len(assistants)} assistant result(s) saved to SQLite",
            f"Winner: {winner_run.assistant.name}",
        ],
        "date": first.created_at.isoformat() if first.created_at else datetime.now().isoformat(),
    }


@router.post("/run")
def run_evaluation(payload: dict, db: Session = Depends(get_db)):
    task_code = payload.get("task_id") or payload.get("task_code")
    assistant_ids = payload.get("assistant_ids") or []

    if not task_code:
        raise HTTPException(status_code=400, detail="task_id is required")

    if not assistant_ids:
        raise HTTPException(status_code=400, detail="assistant_ids is required")

    language_name = payload.get("language", "Python")
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

    task = get_or_create_task(db, task_code)
    language = get_or_create_language(db, language_name)

    saved_runs = []

    for assistant_key in assistant_ids:
        assistant = get_or_create_assistant(db, assistant_key)
        prompt = build_prompt(task_code)
        code = sample_generated_code(task_code, assistant.name)
        metrics = evaluate_code(code, assistant.name, task_code)

        run = EvaluationRun(
            run_id=run_id,
            assistant_id=assistant.id,
            coding_task_id=task.id,
            language_id=language.id,
            status=RunStatus.COMPLETED,
            prompt_text=prompt,
            generated_code=code,
            execution_output=metrics["stdout"],
            execution_error=metrics["runtime_error"] or metrics["syntax_error"],
            execution_success=metrics["runtime_success"],
            execution_time_ms=metrics["execution_time_ms"],
            overall_score=metrics["overall_score"],
            started_at=datetime.now(),
            completed_at=datetime.now(),
        )

        db.add(run)
        db.commit()
        db.refresh(run)

        for finding in metrics["security_findings"]:
            db.add(SecurityFinding(
                evaluation_run_id=run.id,
                category=finding["category"],
                severity=FindingSeverity.HIGH,
                title=finding["title"],
                description=finding["description"],
                recommendation=finding["recommendation"],
            ))

        db.commit()
        db.refresh(run)
        saved_runs.append(run)

    return serialize_run_group(saved_runs)


@router.get("/")
def list_runs(task_id: str | None = None, db: Session = Depends(get_db)):
    query = db.query(EvaluationRun)

    if task_id:
        query = query.join(CodingTask).filter(CodingTask.task_code == task_id)

    runs = query.order_by(EvaluationRun.created_at.desc()).all()

    grouped = {}
    for run in runs:
        grouped.setdefault(run.run_id, []).append(run)

    return {
        "runs": [
            serialize_run_group(group)
            for group in grouped.values()
        ]
    }


@router.get("/{run_id}")
def get_run(run_id: str, db: Session = Depends(get_db)):
    runs = db.query(EvaluationRun).filter(EvaluationRun.run_id == run_id).all()
    return serialize_run_group(runs)


@router.get("/{run_id}/status")
def get_status(run_id: str, db: Session = Depends(get_db)):
    runs = db.query(EvaluationRun).filter(EvaluationRun.run_id == run_id).all()
    return serialize_run_group(runs)


@router.get("/{run_id}/report")
def get_report(run_id: str, format: str = "html", db: Session = Depends(get_db)):
    runs = db.query(EvaluationRun).filter(EvaluationRun.run_id == run_id).all()
    result = serialize_run_group(runs)

    html = f"""
    <html>
        <head><title>Evaluation Report {run_id}</title></head>
        <body>
            <h1>Evaluation Report</h1>
            <p><strong>Run ID:</strong> {run_id}</p>
            <p><strong>Task:</strong> {result["task"]}</p>
            <p><strong>Language:</strong> {result["language"]}</p>
            <p><strong>Winner:</strong> {result["winner"]}</p>
            <h2>Assistant Results</h2>
            <ul>
            {''.join(f'<li>{a["name"]}: {a["score"] * 100}/100</li>' for a in result["assistants"])}
            </ul>
        </body>
    </html>
    """

    return {"run_id": run_id, "format": format, "html": html}