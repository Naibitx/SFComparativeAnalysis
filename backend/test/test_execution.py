"""
End-to-end pipeline test: generation -> execution -> security scan -> metrics.
Uses hardcoded sample code per task to simulate assistant-generated output.
"""

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime
from app.services.execution_engine import run_code
from app.services.security_scanner import scan_code
from app.utils.workspace_manager import create_workspace, save_file
from app.utils.logger import log_info, log_error, log_event
from app.utils.file_utils import save_metadata, save_json


# Simulated assistant-generated code per task (a–h) 

SAMPLE_CODE = {
    "a": """\
with open("sample.txt", "r") as f:
    content = f.read()
print(content)
""",
    "b": """\
import json
import threading

def read_json(filepath):
    with open(filepath, "r") as f:
        return json.load(f)

result = {}
def worker():
    result["data"] = read_json("sample.json")

t = threading.Thread(target=worker)
t.start()
t.join()
print(result)
""",
    "c": """\
with open("output.txt", "w") as f:
    f.write("Hello from AI assistant")
print("File written successfully.")
""",
    "d": """\
import json
import threading

data = {"key": "value", "numbers": [1, 2, 3]}
result = {}

def write_json():
    with open("output.json", "w") as f:
        json.dump(data, f)
    result["status"] = "done"

t = threading.Thread(target=write_json)
t.start()
t.join()
print(result)
""",
    "e": """\
import zipfile
import os

with zipfile.ZipFile("archive.zip", "w") as zf:
    zf.writestr("hello.txt", "Hello from zip")
print("Zip file created.")
""",
    "f": """\
import os

host = os.getenv("DB_HOST", "localhost")
user = os.getenv("DB_USER", "root")
password = os.getenv("DB_PASSWORD", "")
database = os.getenv("DB_NAME", "test")

print(f"Connecting to MySQL at {host} as {user} on database {database}")
print("MySQL connection simulated — no live DB in test environment.")
""",
    "g": """\
import os

uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
database = os.getenv("MONGO_DB", "test")

print(f"Connecting to MongoDB at {uri}, database={database}")
print("MongoDB connection simulated — no live DB in test environment.")
""",
    "h": """\
import hashlib
import os

def hash_password(password: str) -> str:
    salt = os.urandom(16)
    return hashlib.sha256(salt + password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) != hashed  # simplified for simulation

hashed = hash_password("SecurePassword123!")
print(f"Hashed password: {hashed}")
print("Authentication system simulated.")
""",
}

TASK_NAMES = {
    "a": "Read from text file",
    "b": "Read JSON using threads",
    "c": "Write to text file",
    "d": "Write JSON with threads",
    "e": "Create zip file",
    "f": "Connect to MySQL",
    "g": "Connect to MongoDB",
    "h": "Authentication system",
}

MOCK_ASSISTANTS = ["copilot", "chatgpt", "gemini", "grok", "claude"]


# Metrics computation

def compute_metrics(execution: dict, scan: dict) -> dict:
    return {
        "compile_success":      execution.get("exit_code") == 0,
        "timed_out":            execution.get("timed_out", False),
        "duration_ms":          execution.get("duration_ms", 0.0),
        "warnings":             execution.get("warnings", []),
        "warning_count":        len(execution.get("warnings", [])),
        "correctness":          execution.get("correctness", {}),
        "security_total":       scan.get("total", 0),
        "critical_found":       scan.get("critical_found", False),
        "security_findings":    scan.get("findings", []),
    }


# Single pipeline run 

def run_pipeline(task: str, assistant: str) -> dict:
    run_id   = datetime.now().strftime("%Y%m%d_%H%M%S")
    code     = SAMPLE_CODE.get(task, "print('No code defined for this task')")

    # create workspace and save generated code
    workspace  = create_workspace(run_id, task, assistant)
    code_path  = save_file(workspace, "generated_code.py", code)
    save_metadata(workspace, assistant, task, "python")

    log_event("PIPELINE", assistant, task, "started")

    # execution
    execution = run_code(code_path, task)

    # security scan
    scan = scan_code(code_path, assistant, task)

    # metrics
    metrics = compute_metrics(execution, scan)

    # save results to workspace
    save_json(os.path.join(workspace, "execution_result.json"), execution)
    save_json(os.path.join(workspace, "scan_result.json"), scan)
    save_json(os.path.join(workspace, "metrics.json"), metrics)

    log_event("PIPELINE", assistant, task,
              "completed" if execution.get("exit_code") == 0 else "failed")

    return {
        "assistant": assistant,
        "task":      task,
        "workspace": workspace,
        "execution": execution,
        "scan":      scan,
        "metrics":   metrics,
    }


# Result printer 

def print_result(result: dict) -> None:
    e = result["execution"]
    s = result["scan"]
    m = result["metrics"]

    print(f"\n{'='*60}")
    print(f"  Assistant : {result['assistant']}")
    print(f"  Task      : {result['task']} — {TASK_NAMES.get(result['task'], '')}")
    print(f"  Workspace : {result['workspace']}")
    print(f"{'='*60}")
    print(f"  [EXECUTION]")
    print(f"    Exit Code    : {e.get('exit_code')}")
    print(f"    Duration     : {e.get('duration_ms')} ms")
    print(f"    Timed Out    : {e.get('timed_out')}")
    print(f"    Warnings     : {m['warning_count']}")

    correctness = m.get("correctness", {})
    if correctness.get("tested"):
        status = "PASS" if correctness.get("passed") else "FAIL"
        print(f"    Correctness  : {status} (expected={correctness.get('expected')} got={correctness.get('actual')})")
    else:
        print(f"    Correctness  : not tested ({correctness.get('reason', '')})")

    if e.get("stderr"):
        print(f"    Stderr       : {e['stderr'].strip()[:120]}")

    print(f"  [SECURITY]")
    print(f"    Tool         : {s.get('tool')}")
    print(f"    Findings     : {s.get('total')}")
    print(f"    Critical     : {s.get('critical_found')}")
    if s.get("findings"):
        for f in s["findings"]:
            print(f"      [{f['severity']}] {f['vulnerability']} (line {f['line']}) — {f['mitigation']}")


# Full test run 

def run_all_tests() -> None:
    print(f"\nStarting full pipeline test — {len(MOCK_ASSISTANTS)} assistants × {len(SAMPLE_CODE)} tasks\n")
    passed, failed = 0, 0

    for task in SAMPLE_CODE:
        for assistant in MOCK_ASSISTANTS:
            try:
                result = run_pipeline(task, assistant)
                print_result(result)
                passed += 1
            except Exception as e:
                log_error(f"Pipeline error — assistant={assistant} task={task}: {e}")
                print(f"\n[PIPELINE ERROR] assistant={assistant} task={task}: {e}")
                failed += 1

    print(f"\n{'='*60}")
    print(f"  TOTAL: {passed} passed, {failed} failed out of {passed + failed} runs")
    print(f"{'='*60}\n")


# Entry point 

if __name__ == "__main__":
    # single test 
    result = run_pipeline("a", "copilot")
    print_result(result)

    # run_all_tests() - remove "#" to test all of the files