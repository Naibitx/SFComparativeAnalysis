""" Scans generated code for security vulnerabilities using Bandit. """

import subprocess
import sys
import json
import os

from app.utils.logger import log_info, log_error, log_event


def _run_bandit(code_path: str) -> list[dict]:
    # runs bandit on the file and returns a list of parsed findings
    try:
        result = subprocess.run(
            [sys.executable, "-m", "bandit", "-f", "json", "-q", code_path],
            capture_output=True,
            text=True,
        )
        if not result.stdout:
            return []

        data = json.loads(result.stdout)
        findings = []

        for issue in data.get("results", []):
            findings.append({
                "tool":          "bandit",
                "vulnerability": issue.get("test_name", "unknown"),
                "severity":      issue.get("issue_severity", "LOW").upper(),
                "confidence":    issue.get("issue_confidence", "LOW").upper(),
                "description":   issue.get("issue_text", ""),
                "line":          issue.get("line_number"),
                "mitigation":    _get_mitigation(issue.get("test_id", "")),
            })

        return findings

    except Exception as e:
        log_error(f"Bandit scan failed: {e}")
        return []


def _get_mitigation(test_id: str) -> str:
    # maps common bandit test IDs to mitigation notes
    mitigations = {
        "B101": "Avoid assert statements in production code.",
        "B102": "Avoid exec() — use safer alternatives.",
        "B103": "Ensure file permissions are restrictive.",
        "B104": "Avoid binding to all interfaces (0.0.0.0).",
        "B105": "Do not hardcode passwords.",
        "B106": "Do not hardcode passwords in function arguments.",
        "B107": "Do not hardcode passwords in function defaults.",
        "B108": "Insecure temp file — use tempfile module.",
        "B110": "Pass on except: may suppress important errors.",
        "B201": "Flask debug mode should not be enabled in production.",
        "B301": "Pickle is unsafe — avoid deserializing untrusted data.",
        "B303": "MD5/SHA1 are weak — use SHA-256 or stronger.",
        "B304": "Weak cipher detected — use AES with secure mode.",
        "B307": "Avoid eval() — use safer alternatives.",
        "B311": "Random is not cryptographically secure — use secrets module.",
        "B324": "Weak hash function — use SHA-256 or stronger.",
        "B501": "SSL verification bypass disables security.",
        "B601": "Shell injection risk — avoid shell=True with user input.",
        "B602": "Subprocess with shell=True — validate all inputs.",
        "B605": "Starting a process with a shell — validate all arguments.",
        "B608": "Possible SQL injection — use parameterized queries.",
    }
    return mitigations.get(test_id, "Review and address the flagged security issue.")


def _has_critical(findings: list[dict]) -> bool:
    return any(f["severity"] == "HIGH" for f in findings)


def scan_code(code_path: str, assistant: str, task: str) -> dict:
    """ Scans a generated code file and returns structured security results. """
    if not os.path.isfile(code_path):
        log_error(f"scan_code: file not found — {code_path}")
        return _scan_error("File not found.", assistant, task)

    log_info(f"Starting security scan: assistant={assistant} task={task}")

    findings = _run_bandit(code_path)
    critical = _has_critical(findings)

    log_event("SECURITY_SCAN", assistant, task,
              "critical" if critical else "clean",
              f"{len(findings)} finding(s) via bandit")

    return {
        "status":         "success",
        "tool":           "bandit",
        "findings":       findings,
        "total":          len(findings),
        "critical_found": critical,
        "scan_log":       f"Scan completed via bandit. {len(findings)} issue(s) found.",
    }


def _scan_error(reason: str, assistant: str, task: str) -> dict:
    log_event("SECURITY_SCAN", assistant, task, "failed", reason)
    return {
        "status":         "failed",
        "tool":           "none",
        "findings":       [],
        "total":          0,
        "critical_found": False,
        "scan_log":       reason,
    }