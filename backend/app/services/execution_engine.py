"""
Handles toolchain detection, sandbox execution, compile/execute running,
warning collection, and functional correctness validation for Python code.
"""
#check requirements in depth and ensure those are good still
import subprocess
import sys
import os
import ast
import tempfile
import time
import re


TIMEOUT_SECONDS = 10

BLOCKED_IMPORTS = ["shutil", "socket", "requests", "urllib", "ftplib", "smtplib"]

# Expected outputs for functional correctness validation
CORRECTNESS_TESTS = {
    "fibonacci": {
        "inject": "\nprint(fibonacci(10))",
        "expected": "55",
    },
    "bubble_sort": {
        "inject": "\nprint(bubble_sort([5, 3, 1, 4, 2]))",
        "expected": "[1, 2, 3, 4, 5]",
    },
    "binary_search": {
        "inject": "\nprint(binary_search([1, 2, 3, 4, 5], 3))",
        "expected": "2",
    },
}


# Toolchain detector
def detect_toolchain(code: str) -> dict:
    """Detects Python version and key stdlib/third-party imports used."""
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return {"language": "python", "version": sys.version.split()[0], "imports": [], "syntax_error": str(e)}

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports += [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)

    return {
        "language": "python",
        "version": sys.version.split()[0],
        "imports": imports,
        "syntax_error": None,
    }


# Safety check
def _is_safe(code: str) -> tuple[bool, str]:
    for module in BLOCKED_IMPORTS:
        if f"import {module}" in code or f"from {module}" in code:
            return False, f"Blocked import detected: '{module}'"
    return True, ""

# Sandbox execution
def _run_in_sandbox(code: str) -> dict:
    """Runs code in an isolated temp directory subprocess."""
    with tempfile.TemporaryDirectory() as sandbox_dir:
        sandbox_file = os.path.join(sandbox_dir, "solution.py")
        with open(sandbox_file, "w") as f:
            f.write(code)

        start = time.time()
        try:
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
            return _error_result(f"Timed out after {TIMEOUT_SECONDS}s", timed_out=True)


# Warning collector 
def collect_warnings(stderr: str) -> list[str]:
    """Extracts Python warnings from stderr output."""
    warning_pattern = re.compile(r".*Warning.*: .+", re.IGNORECASE)
    return [line.strip() for line in stderr.splitlines() if warning_pattern.match(line)]


# Functional correctness validator
def validate_correctness(code: str, task_code: str) -> dict:
    """Injects a test call and checks output matches expected result."""
    test = CORRECTNESS_TESTS.get(task_code)
    if not test:
        return {"tested": False, "reason": f"No correctness test defined for '{task_code}'"}

    injected_code = code + test["inject"]
    result = _run_in_sandbox(injected_code)
    actual = result["stdout"].strip()
    passed = actual == test["expected"]

    return {
        "tested":   True,
        "passed":   passed,
        "expected": test["expected"],
        "actual":   actual,
    }

# Main entry point 
def run_code(code_path: str, task_code: str = "") -> dict:
    try:
        with open(code_path, "r") as f:
            code = f.read()
    except FileNotFoundError:
        return _error_result(f"File not found: {code_path}")

    toolchain = detect_toolchain(code)
    if toolchain.get("syntax_error"):
        return _error_result(f"Syntax error: {toolchain['syntax_error']}", toolchain=toolchain)

    safe, reason = _is_safe(code)
    if not safe:
        return _error_result(reason, exit_code=2, toolchain=toolchain)

    execution = _run_in_sandbox(code)
    execution["toolchain"]   = toolchain
    execution["warnings"]    = collect_warnings(execution["stderr"])
    execution["correctness"] = validate_correctness(code, task_code) if task_code else {"tested": False, "reason": "No task_code provided"}

    return execution

# Helpers
def _error_result(message: str, exit_code: int = 1, timed_out: bool = False, toolchain: dict = None) -> dict:
    return {
        "exit_code":   exit_code,
        "stdout":      "",
        "stderr":      message,
        "duration_ms": 0.0,
        "timed_out":   timed_out,
        "toolchain":   toolchain or {},
        "warnings":    [],
        "correctness": {"tested": False, "reason": message},
    }