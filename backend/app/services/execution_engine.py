"""
Runs generated code in a sandboxed subprocess with a timeout.
Returns structured execution results to feed into metrics_engine.py.
"""

import subprocess
import sys
import os
import tempfile
import time


TIMEOUT_SECONDS = 10
BLOCKED_IMPORTS = ["shutil", "socket", "requests", "urllib", "ftplib", "smtplib"]


def _is_safe(code: str) -> tuple[bool, str]:
    for module in BLOCKED_IMPORTS:
        if f"import {module}" in code or f"from {module}" in code:
            return False, f"Blocked import detected: '{module}'"
    return True, ""


def run_code(code_path: str) -> dict:
    try:
        with open(code_path, "r") as f:
            code = f.read()
    except FileNotFoundError:
        return _error_result(f"File not found: {code_path}")

    safe, reason = _is_safe(code)
    if not safe:
        return _error_result(reason, exit_code=2)

    try:
        with tempfile.TemporaryDirectory() as sandbox_dir:
            sandbox_file = os.path.join(sandbox_dir, "solution.py")
            with open(sandbox_file, "w") as f:
                f.write(code)

            start = time.time()
            process = subprocess.run(
                [sys.executable, sandbox_file],
                capture_output=True,
                text=True,
                timeout=TIMEOUT_SECONDS,
                cwd=sandbox_dir,
            )
            duration_ms = round((time.time() - start) * 1000, 2)

        return {
            "exit_code":   process.returncode,
            "stdout":      process.stdout,
            "stderr":      process.stderr,
            "duration_ms": duration_ms,
            "timed_out":   False,
        }

    except subprocess.TimeoutExpired:
        return _error_result(
            f"Execution timed out after {TIMEOUT_SECONDS}s",
            exit_code=1,
            timed_out=True,
        )
    except Exception as e:
        return _error_result(str(e))


def _error_result(message: str, exit_code: int = 1, timed_out: bool = False) -> dict:
    return {
        "exit_code":   exit_code,
        "stdout":      "",
        "stderr":      message,
        "duration_ms": 0.0,
        "timed_out":   timed_out,
    }