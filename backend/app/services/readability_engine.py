"""
readability_engine.py
---------------------
Static readability analysis for Python code.

Produces a result dict that slots directly into MetricsEngine.evaluate_assistant()
via the `readability_result` parameter:

    {
        "available": True,
        "score": 0-100,          # weighted composite
        "breakdown": { ... },    # per-metric raw values and scores
        "notes": [ ... ],        # human-readable observations
        "error": None,
    }
"""
from __future__ import annotations

import ast
import re
import tokenize
import io
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

def _lines(code: str) -> list[str]:
    return code.splitlines()


def _nonempty_lines(code: str) -> list[str]:
    return [l for l in _lines(code) if l.strip()]


def _comment_lines(code: str) -> list[str]:
    """Lines that are purely a comment (stripped starts with #)."""
    return [l for l in _lines(code) if l.strip().startswith("#")]


def _tokens(code: str) -> list[tokenize.TokenInfo]:
    try:
        return list(tokenize.generate_tokens(io.StringIO(code).readline))
    except tokenize.TokenError:
        return []


# ---------------------------------------------------------------------------
# Individual metric functions
# Return a (raw_value, score_0_to_100, notes) tuple.
# ---------------------------------------------------------------------------

def _metric_comment_ratio(code: str) -> tuple[float, float, list[str]]:
    """
    Ratio of comment lines to non-empty lines.
    Ideal band: 10 – 30 %.  Score peaks at 20 %.
    """
    total = len(_nonempty_lines(code))
    if total == 0:
        return 0.0, 0.0, ["No code found."]

    comments = len(_comment_lines(code))
    ratio = comments / total  # 0..1

    # Triangle that peaks at 0.20 and falls off toward 0 and 0.50+
    if ratio <= 0.20:
        score = (ratio / 0.20) * 100
    else:
        score = max(0.0, 100 - ((ratio - 0.20) / 0.30) * 100)

    notes = []
    if ratio < 0.05:
        notes.append(f"Very few comments ({ratio:.0%} of lines). Consider adding docstrings or inline comments.")
    elif ratio > 0.40:
        notes.append(f"High comment density ({ratio:.0%}). Some comments may be redundant.")
    else:
        notes.append(f"Comment ratio is {ratio:.0%} — within a healthy range.")

    return round(ratio, 4), round(score, 2), notes


def _metric_docstring_coverage(code: str) -> tuple[float, float, list[str]]:
    """
    Fraction of functions/classes that have a docstring.
    Score = coverage * 100.
    """
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return 0.0, 0.0, ["Could not parse code; docstring coverage skipped."]

    definitions: list[ast.AST] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            definitions.append(node)

    if not definitions:
        return 1.0, 100.0, ["No functions or classes found — full docstring credit awarded."]

    documented = sum(
        1 for d in definitions if ast.get_docstring(d)
    )
    coverage = documented / len(definitions)
    score = round(coverage * 100, 2)

    notes = []
    if coverage < 0.5:
        undoc = len(definitions) - documented
        notes.append(f"{undoc}/{len(definitions)} functions/classes lack docstrings.")
    elif coverage < 1.0:
        notes.append(f"Docstring coverage: {coverage:.0%}. A few items are undocumented.")
    else:
        notes.append("All functions and classes are documented.")

    return round(coverage, 4), score, notes


def _metric_avg_function_length(code: str) -> tuple[float, float, list[str]]:
    """
    Average lines per function/method.
    Ideal ≤ 20 lines.  Score degrades linearly to 0 at 60 lines.
    """
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return 0.0, 0.0, ["Could not parse code; function-length check skipped."]

    lengths = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # end_lineno is available in Python 3.8+
            start = node.lineno
            end = getattr(node, "end_lineno", node.lineno)
            lengths.append(end - start + 1)

    if not lengths:
        return 0.0, 100.0, ["No functions found — function-length credit awarded."]

    avg = sum(lengths) / len(lengths)

    if avg <= 20:
        score = 100.0
    elif avg >= 60:
        score = 0.0
    else:
        score = round(100 - ((avg - 20) / 40) * 100, 2)

    notes = []
    if avg > 40:
        notes.append(f"Average function length is {avg:.1f} lines — consider breaking large functions apart.")
    elif avg > 20:
        notes.append(f"Average function length is {avg:.1f} lines — slightly long but manageable.")
    else:
        notes.append(f"Average function length is {avg:.1f} lines — concise and readable.")

    return round(avg, 2), score, notes


def _metric_avg_line_length(code: str) -> tuple[float, float, list[str]]:
    """
    Average characters per non-empty line.
    PEP 8 recommends ≤ 79.  Score degrades beyond 79 and 0 at 120.
    """
    nonempty = _nonempty_lines(code)
    if not nonempty:
        return 0.0, 100.0, []

    avg = sum(len(l) for l in nonempty) / len(nonempty)

    if avg <= 79:
        score = 100.0
    elif avg >= 120:
        score = 0.0
    else:
        score = round(100 - ((avg - 79) / 41) * 100, 2)

    long_lines = [l for l in _lines(code) if len(l) > 79]
    pct_long = len(long_lines) / len(nonempty)

    notes = []
    if pct_long > 0.20:
        notes.append(
            f"{pct_long:.0%} of lines exceed 79 characters (PEP 8 recommendation). "
            "Consider breaking long expressions."
        )
    else:
        notes.append(f"Average line length is {avg:.1f} chars — within PEP 8 limits.")

    return round(avg, 2), score, notes


def _metric_naming_conventions(code: str) -> tuple[float, float, list[str]]:
    """
    Checks that:
      - functions/methods use snake_case
      - classes use PascalCase
      - constants (module-level ALL_CAPS) are allowed
    Score = fraction of names that conform * 100.
    """
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return 0.0, 0.0, ["Could not parse code; naming check skipped."]

    snake_re = re.compile(r"^[a-z_][a-z0-9_]*$")
    pascal_re = re.compile(r"^[A-Z][a-zA-Z0-9]*$")

    violations = []
    total = 0

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            total += 1
            if not snake_re.match(node.name):
                violations.append(f"Function '{node.name}' should be snake_case.")
        elif isinstance(node, ast.ClassDef):
            total += 1
            if not pascal_re.match(node.name):
                violations.append(f"Class '{node.name}' should be PascalCase.")

    if total == 0:
        return 1.0, 100.0, ["No named definitions to check."]

    conformance = (total - len(violations)) / total
    score = round(conformance * 100, 2)

    notes = violations[:5]  # cap to avoid noise
    if not violations:
        notes = ["All function and class names follow Python naming conventions."]
    elif len(violations) > 5:
        notes.append(f"… and {len(violations) - 5} more naming issues.")

    return round(conformance, 4), score, notes


def _metric_complexity(code: str) -> tuple[float, float, list[str]]:
    """
    Approximates McCabe cyclomatic complexity per function.
    Counts branching AST nodes (If, For, While, ExceptHandler, With,
    comprehensions, BoolOp arms).
    Score degrades linearly: avg complexity 1 → 100, avg ≥ 10 → 0.
    """
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return 0.0, 0.0, ["Could not parse code; complexity check skipped."]

    BRANCH_NODES = (
        ast.If, ast.For, ast.While, ast.ExceptHandler,
        ast.With, ast.ListComp, ast.SetComp, ast.DictComp,
        ast.GeneratorExp,
    )

    function_complexities: list[float] = []

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue

        complexity = 1  # base path
        for child in ast.walk(node):
            if isinstance(child, BRANCH_NODES):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                # each extra operand adds a branch
                complexity += len(child.values) - 1

        function_complexities.append(complexity)

    if not function_complexities:
        return 0.0, 100.0, ["No functions found — complexity credit awarded."]

    avg = sum(function_complexities) / len(function_complexities)
    high_cc = [c for c in function_complexities if c >= 10]

    if avg <= 1:
        score = 100.0
    elif avg >= 10:
        score = 0.0
    else:
        score = round(100 - ((avg - 1) / 9) * 100, 2)

    notes = []
    if high_cc:
        notes.append(
            f"{len(high_cc)} function(s) have cyclomatic complexity ≥ 10 — "
            "consider refactoring."
        )
    if avg > 5:
        notes.append(f"Average complexity is {avg:.1f}. Aim for ≤ 5 per function.")
    else:
        notes.append(f"Average cyclomatic complexity is {avg:.1f} — good.")

    return round(avg, 2), score, notes


def _metric_magic_numbers(code: str) -> tuple[int, float, list[str]]:
    """
    Counts numeric literals that are not 0, 1, -1, or 2 and are not
    inside a constant assignment (ALL_CAPS = ...).
    Score: 0 magic numbers → 100, each one deducts up to 10 pts, floor 0.
    """
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return 0, 0.0, ["Could not parse code; magic-number check skipped."]

    ALLOWED = {0, 1, -1, 2}

    # Collect names of module-level constants (ALL_CAPS assignments)
    constant_names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id.isupper():
                    constant_names.add(t.id)

    magic_count = 0
    for node in ast.walk(tree):
        # Skip if inside a constant assignment value
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            if node.value not in ALLOWED:
                magic_count += 1

    score = max(0.0, round(100 - magic_count * 10, 2))

    notes = []
    if magic_count == 0:
        notes.append("No magic numbers detected.")
    elif magic_count <= 3:
        notes.append(f"{magic_count} magic number(s) found. Consider naming them as constants.")
    else:
        notes.append(
            f"{magic_count} magic numbers found. Extract them into named constants for clarity."
        )

    return magic_count, score, notes


# ---------------------------------------------------------------------------
# Weights for the composite score
# ---------------------------------------------------------------------------

WEIGHTS = {
    "comment_ratio":       0.15,
    "docstring_coverage":  0.25,
    "avg_function_length": 0.20,
    "avg_line_length":     0.10,
    "naming_conventions":  0.15,
    "complexity":          0.10,
    "magic_numbers":       0.05,
}

assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9, "Weights must sum to 1.0"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class ReadabilityEngine:
    """
    Analyse Python source code for readability.

    Usage
    -----
        engine = ReadabilityEngine()
        result = engine.analyse(code)

    Plug into MetricsEngine
    -----------------------
        metrics = MetricsEngine()
        readability = ReadabilityEngine().analyse(assistant_code)
        result = metrics.evaluate_assistant(
            assistant=my_assistant,
            prompt="...",
            readability_result=readability,
        )
    """

    def analyse(self, code: str) -> dict:
        """
        Run all readability metrics and return a result dict.

        The returned dict has the shape expected by MetricsEngine:
            {
                "available": True,
                "score": float,        # 0-100 composite
                "breakdown": { ... },  # per-metric details
                "notes": [ ... ],      # all human-readable messages
                "error": None,
            }
        """
        if not code or not code.strip():
            return {
                "available": False,
                "score": None,
                "breakdown": {},
                "notes": [],
                "error": "Empty code string provided.",
            }

        metrics = {
            "comment_ratio":       _metric_comment_ratio(code),
            "docstring_coverage":  _metric_docstring_coverage(code),
            "avg_function_length": _metric_avg_function_length(code),
            "avg_line_length":     _metric_avg_line_length(code),
            "naming_conventions":  _metric_naming_conventions(code),
            "complexity":          _metric_complexity(code),
            "magic_numbers":       _metric_magic_numbers(code),
        }

        breakdown: dict[str, dict] = {}
        all_notes: list[str] = []
        composite = 0.0

        for name, (raw_value, metric_score, notes) in metrics.items():
            weight = WEIGHTS[name]
            breakdown[name] = {
                "raw": raw_value,
                "score": metric_score,
                "weight": weight,
                "weighted_score": round(metric_score * weight, 4),
            }
            composite += metric_score * weight
            all_notes.extend(notes)

        return {
            "available": True,
            "score": round(composite, 2),
            "breakdown": breakdown,
            "notes": all_notes,
            "error": None,
        }

    def analyse_many(self, named_codes: dict[str, str]) -> dict[str, dict]:
        """
        Analyse multiple assistants' outputs at once.

        Parameters
        ----------
        named_codes : { assistant_name: code_string }

        Returns
        -------
        { assistant_name: readability_result }

        Pass the return value directly to MetricsEngine.compare_assistants()
        as `readability_results`.
        """
        return {name: self.analyse(code) for name, code in named_codes.items()}