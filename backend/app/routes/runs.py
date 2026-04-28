from datetime import datetime
import ast
import subprocess
import sys
import tempfile
from pathlib import Path
import tracemalloc

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.integrations.assistant_factory import get_assistant_client
from app.Models.assistant import Assistant
from app.Models.coding_task import CodingTask
from app.Models.language import Language, LanguageCategory
from app.Models.evaluation_run import EvaluationRun, RunStatus
from app.Models.security_finding import SecurityFinding, FindingSeverity
from app.services.prompt_builder import build_prompt
from app.services.readability_engine import ReadabilityEngine

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

LANGUAGE_EXTENSIONS = {
    "Python": ".py",
    "JavaScript": ".js",
    "PHP": ".php",
    "Java": ".java",
    "C++": ".cpp",
}


def make_slug(value: str) -> str:
    return (
        value.lower()
        .replace("++", "pp")
        .replace("#", "sharp")
        .replace(" ", "_")
        .replace("-", "_")
    )


def get_or_create_assistant(db: Session, assistant_key: str) -> Assistant:
    name = ASSISTANT_NAMES.get(assistant_key, assistant_key.title())

    assistant = db.query(Assistant).filter(Assistant.name == name).first()
    if assistant:
        return assistant

    assistant = Assistant(
        name=name,
        provider=name,
        model_version="openrouter",
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

    language = Language(
        name=language_name,
        slug=make_slug(language_name),
        file_extension=LANGUAGE_EXTENSIONS.get(language_name),
        category=LanguageCategory.SCRIPTING,
        description=f"{language_name} language used for generated-code evaluations.",
    )

    db.add(language)
    db.commit()
    db.refresh(language)
    return language


def get_or_create_task(db: Session, task_code: str) -> CodingTask:
    task_code = task_code.lower()

    task = db.query(CodingTask).filter(CodingTask.task_code == task_code).first()
    if task:
        return task

    prompt = build_prompt(task_code)

    task = CodingTask(
        task_code=task_code,
        name=TASK_NAMES.get(task_code, f"Task {task_code.upper()}"),
        description=prompt,
        prompt_template=prompt,
        difficulty_level=1,
        default_language_id=None,
    )

    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def normalize_task_a_code(code: str, input_file: str) -> str:
    replacements = [
        "example.txt",
        "your_file.txt",
        "my_text_file.txt",
        "file.txt",
        "input.txt",
        "sample.txt",
        "sample_input.txt",
    ]

    for name in replacements:
        code = code.replace(f'"{name}"', f'"{input_file}"')
        code = code.replace(f"'{name}'", f"'{input_file}'")

    return code


def normalize_task_b_code(code: str, input_file: str) -> str:
    replacements = [
        "data.json",
        "sample.json",
        "input.json",
        "file.json",
        "sample_data.json",
    ]

    for name in replacements:
        code = code.replace(f'"{name}"', f'"{input_file}"')
        code = code.replace(f"'{name}'", f"'{input_file}'")

    return code


def normalize_task_e_code(code: str, input_file: str) -> str:
    replacements = [
        "input.txt",
        "sample.txt",
        "example.txt",
        "my_text_file.txt",
        "file.txt",
    ]

    for name in replacements:
        code = code.replace(f'"{name}"', f'"{input_file}"')
        code = code.replace(f"'{name}'", f"'{input_file}'")

    return code


def evaluate_code(code: str, language_name: str = "Python") -> dict:
    syntax_success = True
    syntax_error = None
    runtime_success = False
    runtime_error = None
    stdout = ""
    execution_time_ms = None
    memory_mb = None

    if language_name == "Python":
        try:
            ast.parse(code)
        except SyntaxError as exc:
            syntax_success = False
            syntax_error = str(exc)

        if syntax_success:
            with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as temp:
                temp.write(code)
                temp_path = temp.name

            started = datetime.now()

            try:
                tracemalloc.start()

                completed = subprocess.run(
                    [sys.executable, temp_path],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                current, peak = tracemalloc.get_traced_memory()
                memory_mb = round(peak / (1024 * 1024), 2)
                tracemalloc.stop()

                ended = datetime.now()
                execution_time_ms = round((ended - started).total_seconds() * 1000, 2)
                stdout = completed.stdout
                runtime_success = completed.returncode == 0
                runtime_error = completed.stderr if completed.returncode != 0 else None

            except Exception as exc:
                runtime_error = str(exc)
                try:
                    tracemalloc.stop()
                except RuntimeError:
                    pass

            Path(temp_path).unlink(missing_ok=True)

    else:
        syntax_success = True
        runtime_success = True
        stdout = f"{language_name} code saved. Runtime execution is not enabled for this language yet."
        execution_time_ms = 0
        memory_mb = 0

    try:
        readability = readability_engine.analyse(code)
        readability_score = readability.get("score") or 0
    except Exception:
        readability_score = 70

    warnings = 0
    findings = []

    if "eval(" in code or "exec(" in code:
        warnings += 1
        findings.append({
            "category": "Unsafe Execution",
            "severity": FindingSeverity.HIGH,
            "title": "Unsafe dynamic execution",
            "description": "Code contains eval() or exec().",
            "recommendation": "Avoid dynamic execution unless absolutely necessary.",
        })

    if "shell=True" in code:
        warnings += 1
        findings.append({
            "category": "Command Injection",
            "severity": FindingSeverity.HIGH,
            "title": "shell=True detected",
            "description": "Subprocess shell execution can be dangerous.",
            "recommendation": "Use argument lists and avoid shell=True.",
        })

    if "import anthropic" in code.lower() or "anthropic.anthropic" in code.lower():
        warnings += 1
        findings.append({
            "category": "AI API Misuse",
            "severity": FindingSeverity.HIGH,
            "title": "Generated code imports Anthropic SDK",
            "description": "Generated benchmark code should not call AI APIs.",
            "recommendation": "Prompt should forbid AI SDK usage and generated code should be standalone.",
        })

    syntax_score = 100 if syntax_success else 0
    runtime_score = 100 if runtime_success else 0
    security_score = max(0, 100 - warnings * 25)

    overall_score = round(
        syntax_score * 0.30
        + runtime_score * 0.25
        + readability_score * 0.25
        + security_score * 0.20,
        2,
    )

    return {
        "syntax_success": syntax_success,
        "syntax_error": syntax_error,
        "runtime_success": runtime_success,
        "runtime_error": runtime_error,
        "stdout": stdout,
        "execution_time_ms": execution_time_ms,
        "memory_mb": memory_mb,
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
        score_100 = run.overall_score or 0
        score_normalized = round(score_100 / 100, 2)

        assistants.append({
            "id": run.assistant.name.lower().replace(" ", "_"),
            "name": run.assistant.name,
            "status": run.status.value if hasattr(run.status, "value") else str(run.status),
            "progress": 100,
            "compile": run.execution_error is None,
            "correct": run.execution_success,
            "warnings": findings_count,
            "time_ms": run.execution_time_ms,
            "memory_mb": run.memory_mb,
            "readability": run.readability_score,
            "readability_score": run.readability_score,
            "security": findings_count,
            "score": score_normalized,
            "score_raw": score_100,
            "code": run.generated_code or "",
            "output": run.execution_output or "",
            "error": run.execution_error,
        })

    assistants = sorted(
        assistants,
        key=lambda a: (
            a["correct"],
            a["compile"],
            a["score_raw"],
            -(a["security"]),
            -(a["time_ms"] or 999999),
        ),
        reverse=True,
    )

    winner = assistants[0]

    task_name = first.coding_task.name if first.coding_task else "Unknown Task"
    task_code = first.coding_task.task_code if first.coding_task else ""

    return {
        "run_id": first.run_id,
        "id": first.run_id,
        "task": task_name,
        "task_id": task_code,
        "language": first.language.name if first.language else "Python",
        "overall_status": "completed",
        "status": "completed",
        "winner": winner["name"],
        "winner_score": winner["score"],
        "winner_justification": (
            f"{winner['name']} had the best result based on correctness, compilation, "
            f"overall score, security, and execution time."
        ),
        "assistants": assistants,
        "logs": [
            f"Evaluation completed for {task_name}",
            f"{len(assistants)} assistant result(s) saved to SQLite",
            f"Winner: {winner['name']}",
        ],
        "date": first.created_at.isoformat() if first.created_at else datetime.now().isoformat(),
    }


@router.post("/run")
def run_evaluation(payload: dict, db: Session = Depends(get_db)):
    task_code = payload.get("task_id") or payload.get("task_code")
    assistant_ids = payload.get("assistant_ids") or []
    language_name = payload.get("language", "Python")
    input_file = payload.get("input_file") or "sample_input.txt"

    if not task_code:
        raise HTTPException(status_code=400, detail="task_id is required")

    if not assistant_ids:
        raise HTTPException(status_code=400, detail="assistant_ids is required")

    task_code = task_code.lower()
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

    task = get_or_create_task(db, task_code)
    language = get_or_create_language(db, language_name)

    saved_runs = []

    for assistant_key in assistant_ids:
        assistant = get_or_create_assistant(db, assistant_key)
        prompt = build_prompt(task_code)

        if task_code in ["a", "b", "e"]:
            prompt += f"""

Important runtime input:
- Use this exact input file path: {input_file}
- Do not use placeholder file names.
"""

        assistant_client = get_assistant_client(assistant_key)
        generation = assistant_client.generate_code(prompt, language_name)

        if "code" in generation:
            code = generation["code"]
            tokens_used = generation.get("tokens_used")
            latency_ms = generation.get("latency_ms")
        else:
            code = f"# Generation failed for {assistant.name}\nprint('Generation failed')"
            tokens_used = None
            latency_ms = None

        if language_name == "Python":
            if task_code == "a":
                code = normalize_task_a_code(code, input_file)
            elif task_code == "b":
                code = normalize_task_b_code(code, input_file)
            elif task_code == "e":
                code = normalize_task_e_code(code, input_file)

        metrics = evaluate_code(code, language_name)

        run = EvaluationRun(
            run_id=run_id,
            assistant_id=assistant.id,
            coding_task_id=task.id,
            language_id=language.id,
            status=RunStatus.COMPLETED,
            workspace_path=None,
            prompt_text=prompt,
            generated_code_path=None,
            generated_code=code,
            execution_output=metrics["stdout"],
            execution_error=metrics["runtime_error"] or metrics["syntax_error"],
            execution_success=metrics["runtime_success"],
            tokens_used=tokens_used,
            latency_ms=latency_ms,
            execution_time_ms=metrics["execution_time_ms"],
            memory_mb=metrics["memory_mb"],
            readability_score=metrics["readability_score"],
            overall_score=metrics["overall_score"],
            started_at=datetime.now(),
            completed_at=datetime.now(),
        )

        db.add(run)
        db.commit()
        db.refresh(run)

        for finding in metrics["security_findings"]:
            security_finding = SecurityFinding(
                evaluation_run_id=run.id,
                category=finding["category"],
                severity=finding["severity"],
                title=finding["title"],
                description=finding["description"],
                recommendation=finding["recommendation"],
                file_path=None,
                line_number=None,
            )
            db.add(security_finding)

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

    return {
        "run_id": run_id,
        "format": format,
        "html": html,
    }