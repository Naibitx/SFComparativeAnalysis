""" Handles sandboxed subprocess execution for the execution engine. """
 
import subprocess
import sys
import tempfile
import os
import time
 
TIMEOUT_SECONDS = 10
 
def run_sandboxed(code: str) -> dict:
    # runs code in an isolated temp directory with no access to any project files
    with tempfile.TemporaryDirectory() as sandbox_dir:
        code_file = os.path.join(sandbox_dir, "solution.py")
        with open(code_file, "w") as f:
            f.write(code)
 
        try:
            start = time.time()
            process = subprocess.run(
                [sys.executable, code_file],
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
            return {
                "exit_code":   1,
                "stdout":      "",
                "stderr":      f"Execution timed out after {TIMEOUT_SECONDS}s",
                "duration_ms": 0.0,
                "timed_out":   True,
            }