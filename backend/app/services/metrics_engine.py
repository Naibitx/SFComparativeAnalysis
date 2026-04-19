"""
metrics_engine.py
-----------------
Runs evaluations on assistants that inherit from BaseAssistant.
"""

from __future__ import annotations

import ast
import io
import time
import traceback
import contextlib
from dataclasses import dataclass
from typing import Any, Optional

from base_assistant import BaseAssistant


@dataclass
class TestCase:
    input_data: Any
    expected_output: Any
    description: str = ""


class MetricsEngine:
    def __init__(self) -> None:
        pass

    def evaluate_assistant(
        self,
        assistant: BaseAssistant,
        prompt: str,
        language: str = "python",
        context: Optional[str] = None,
        test_cases: Optional[list[TestCase]] = None,
        entry_function: Optional[str] = None,
        readability_result: Optional[dict] = None,
        security_result: Optional[dict] = None,
    ) -> dict:
        # Start total timer
        total_start = time.perf_counter()

        # Ask the assistant to generate code
        try:
            response = assistant.generate_code(
                prompt=prompt,
                language=language,
                context=context,
            )
        except Exception as exc:
            return {
                "assistant": assistant.name,
                "provider": assistant.provider,
                "language": language,
                "generation_success": False,
                "generation_error": str(exc),
                "evaluation_success": False,
                "overall_score": 0.0,
                "timestamp": time.time(),
            }

        # Make sure the response is a dict
        if not isinstance(response, dict):
            return {
                "assistant": assistant.name,
                "provider": assistant.provider,
                "language": language,
                "generation_success": False,
                "generation_error": "generate_code did not return a dict",
                "evaluation_success": False,
                "overall_score": 0.0,
                "timestamp": time.time(),
            }

        code = response.get("code", "")
        explanation = response.get("explanation", "")
        tokens_used = response.get("tokens_used")
        latency_ms = response.get("latency_ms")

        # Right now this engine is only for Python
        if language.lower() != "python":
            return {
                "assistant": assistant.name,
                "provider": assistant.provider,
                "language": language,
                "generation_success": True,
                "evaluation_success": False,
                "code": code,
                "explanation": explanation,
                "tokens_used": tokens_used,
                "latency_ms": latency_ms,
                "error": "MetricsEngine currently supports python only",
                "overall_score": 0.0,
                "timestamp": time.time(),
            }

        # Run checks
        syntax_result = self._check_python_syntax(code)
        runtime_result = self._check_python_runtime(code)
        correctness_result = self._check_functional_correctness(
            code=code,
            test_cases=test_cases or [],
            entry_function=entry_function,
        )

        # Use passed-in readability result if available
        if readability_result is None:
            readability_result = self._default_readability_result()

        # Use passed-in security result if available
        if security_result is None:
            security_result = self._default_security_result()

        overall_score = self._compute_overall_score(
            syntax_result=syntax_result,
            runtime_result=runtime_result,
            correctness_result=correctness_result,
            readability_result=readability_result,
            security_result=security_result,
        )

        total_end = time.perf_counter()

        return {
            "assistant": assistant.name,
            "provider": assistant.provider,
            "language": language,
            "generation_success": True,
            "evaluation_success": True,
            "code": code,
            "explanation": explanation,
            "tokens_used": tokens_used,
            "latency_ms": latency_ms,
            "evaluation_time_ms": round((total_end - total_start) * 1000, 3),
            "syntax": syntax_result,
            "runtime": runtime_result,
            "correctness": correctness_result,
            "readability": readability_result,
            "security": security_result,
            "overall_score": overall_score,
            "timestamp": time.time(),
        }

    def compare_assistants(
        self,
        assistants: list[BaseAssistant],
        prompt: str,
        language: str = "python",
        context: Optional[str] = None,
        test_cases: Optional[list[TestCase]] = None,
        entry_function: Optional[str] = None,
        readability_results: Optional[dict[str, dict]] = None,
        security_results: Optional[dict[str, dict]] = None,
    ) -> list[dict]:
        results = []

        for assistant in assistants:
            assistant_readability = None
            assistant_security = None

            if readability_results is not None:
                assistant_readability = readability_results.get(assistant.name)

            if security_results is not None:
                assistant_security = security_results.get(assistant.name)

            result = self.evaluate_assistant(
                assistant=assistant,
                prompt=prompt,
                language=language,
                context=context,
                test_cases=test_cases,
                entry_function=entry_function,
                readability_result=assistant_readability,
                security_result=assistant_security,
            )
            results.append(result)

        results.sort(key=lambda item: item.get("overall_score", 0.0), reverse=True)
        return results

    def _check_python_syntax(self, code: str) -> dict:
        # Check if Python code parses correctly
        try:
            ast.parse(code)
            return {
                "success": True,
                "error": None,
                "warnings": [],
            }
        except SyntaxError as exc:
            return {
                "success": False,
                "error": f"{exc.__class__.__name__}: {exc}",
                "warnings": [],
            }

    def _check_python_runtime(self, code: str) -> dict:
        # Run the code and capture output
        namespace: dict[str, Any] = {}
        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()

        start = time.perf_counter()

        try:
            with contextlib.redirect_stdout(stdout_buffer), contextlib.redirect_stderr(stderr_buffer):
                exec(code, namespace, namespace)

            end = time.perf_counter()

            return {
                "success": True,
                "stdout": stdout_buffer.getvalue(),
                "stderr": stderr_buffer.getvalue(),
                "error": None,
                "execution_time_ms": round((end - start) * 1000, 3),
            }

        except Exception as exc:
            end = time.perf_counter()

            return {
                "success": False,
                "stdout": stdout_buffer.getvalue(),
                "stderr": stderr_buffer.getvalue(),
                "error": "".join(traceback.format_exception_only(type(exc), exc)).strip(),
                "execution_time_ms": round((end - start) * 1000, 3),
            }

    def _check_functional_correctness(
        self,
        code: str,
        test_cases: list[TestCase],
        entry_function: Optional[str],
    ) -> dict:
        # If there are no tests, skip correctness
        if not test_cases:
            return {
                "available": False,
                "passed": 0,
                "total": 0,
                "score": None,
                "details": [],
                "error": "No test cases provided",
            }

        # If no function name is given, skip correctness
        if not entry_function:
            return {
                "available": False,
                "passed": 0,
                "total": len(test_cases),
                "score": None,
                "details": [],
                "error": "No entry_function provided",
            }

        namespace: dict[str, Any] = {}

        # Load the generated code
        try:
            exec(code, namespace, namespace)
        except Exception as exc:
            return {
                "available": True,
                "passed": 0,
                "total": len(test_cases),
                "score": 0.0,
                "details": [],
                "error": f"Generated code could not be loaded: {exc}",
            }

        target = namespace.get(entry_function)

        # Make sure the target function exists
        if not callable(target):
            return {
                "available": True,
                "passed": 0,
                "total": len(test_cases),
                "score": 0.0,
                "details": [],
                "error": f"Function '{entry_function}' not found or not callable",
            }

        passed = 0
        details = []

        # Run each test
        for index, case in enumerate(test_cases, start=1):
            try:
                if isinstance(case.input_data, tuple):
                    actual = target(*case.input_data)
                else:
                    actual = target(case.input_data)

                test_passed = actual == case.expected_output

                if test_passed:
                    passed += 1

                details.append({
                    "test_number": index,
                    "description": case.description,
                    "input": case.input_data,
                    "expected": case.expected_output,
                    "actual": actual,
                    "passed": test_passed,
                })

            except Exception as exc:
                details.append({
                    "test_number": index,
                    "description": case.description,
                    "input": case.input_data,
                    "expected": case.expected_output,
                    "actual": None,
                    "passed": False,
                    "error": str(exc),
                })

        score = round((passed / len(test_cases)) * 100, 2)

        return {
            "available": True,
            "passed": passed,
            "total": len(test_cases),
            "score": score,
            "details": details,
            "error": None,
        }

    def _default_readability_result(self) -> dict:
        # Placeholder until readability module is connected
        return {
            "available": False,
            "score": None,
            "notes": [],
            "error": "Readability analysis not run yet",
        }

    def _default_security_result(self) -> dict:
        # Placeholder until Coverity is connected
        return {
            "available": False,
            "tool": "Coverity",
            "score": None,
            "findings": [],
            "error": "Security scan not run yet",
        }

    def _compute_overall_score(
        self,
        syntax_result: dict,
        runtime_result: dict,
        correctness_result: dict,
        readability_result: dict,
        security_result: dict,
    ) -> float:
        syntax_score = 100.0 if syntax_result.get("success") else 0.0
        runtime_score = 100.0 if runtime_result.get("success") else 0.0

        correctness_score = correctness_result.get("score")
        if correctness_score is None:
            correctness_score = 0.0

        readability_score = readability_result.get("score")
        readability_available = (
            readability_result.get("available") and readability_score is not None
        )

        security_score = security_result.get("score")
        security_available = (
            security_result.get("available") and security_score is not None
        )

        # Use full weights if everything is available
        if readability_available and security_available:
            overall = (
                syntax_score * 0.15 +
                runtime_score * 0.15 +
                correctness_score * 0.35 +
                readability_score * 0.15 +
                security_score * 0.20
            )
            return round(overall, 2)

        # Use readability, skip security
        if readability_available and not security_available:
            overall = (
                syntax_score * 0.20 +
                runtime_score * 0.20 +
                correctness_score * 0.40 +
                readability_score * 0.20
            )
            return round(overall, 2)

        # Use security, skip readability
        if security_available and not readability_available:
            overall = (
                syntax_score * 0.20 +
                runtime_score * 0.20 +
                correctness_score * 0.40 +
                security_score * 0.20
            )
            return round(overall, 2)

        # Only use syntax, runtime, correctness
        overall = (
            syntax_score * 0.25 +
            runtime_score * 0.25 +
            correctness_score * 0.50
        )
        return round(overall, 2)