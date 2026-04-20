# AI Assistant Comparison Report

{% set report_title = title or "AI Assistant Comparison Report" %}
{% set run_items = runs if runs is defined and runs else [] %}
{% set generated_at_value = generated_at or timestamp or "N/A" %}
{% set task_name_value = task_name or task.name if task is defined and task else "N/A" %}
{% set task_code_value = task_code or task.task_code if task is defined and task else "N/A" %}
{% set language_value = language or (task.default_language.name if task is defined and task.default_language else "N/A") %}

## {{ report_title }}

**Generated At:** {{ generated_at_value }}  
**Task:** {{ task_name_value }}  
**Task Code:** {{ task_code_value }}  
**Language:** {{ language_value }}

{% if summary is defined and summary %}
## Executive Summary

- Total Assistants Compared: {{ summary.total_assistants or run_items|length }}
- Successful Executions: {{ summary.successful_executions or 0 }}
- Failed Executions: {{ summary.failed_executions or 0 }}
- Best Overall Score: {{ summary.best_score or "N/A" }}
- Top Assistant: {{ summary.top_assistant or "N/A" }}
{% elif run_items %}
## Executive Summary

- Total Assistants Compared: {{ run_items|length }}
- Successful Executions: {{ run_items | selectattr("execution_success") | list | length }}
- Failed Executions: {{ run_items | rejectattr("execution_success") | list | length }}
{% endif %}

{% if run_items %}
## Results Overview

| Assistant | Provider | Status | Overall Score | Tokens Used | Latency (ms) | Execution Time (ms) |
| --- | --- | --- | ---: | ---: | ---: | ---: |
{% for run in run_items %}
| {{ run.assistant.name if run.assistant is defined and run.assistant else run.assistant_name or run.assistant or "Unknown" }} | {{ run.assistant.provider if run.assistant is defined and run.assistant else run.provider or "N/A" }} | {{ run.status.value if run.status is defined and run.status and run.status.value is defined else run.status or ("completed" if run.execution_success else "failed") }} | {{ run.overall_score if run.overall_score is not none else "N/A" }} | {{ run.tokens_used if run.tokens_used is not none else "N/A" }} | {{ run.latency_ms if run.latency_ms is not none else "N/A" }} | {{ run.execution_time_ms if run.execution_time_ms is not none else "N/A" }} |
{% endfor %}
{% endif %}

{% for run in run_items %}
---

## {{ run.assistant.name if run.assistant is defined and run.assistant else run.assistant_name or run.assistant or "Assistant Result" }}

**Provider:** {{ run.assistant.provider if run.assistant is defined and run.assistant else run.provider or "N/A" }}  
**Run ID:** {{ run.run_id or run.id or "N/A" }}  
**Status:** {{ run.status.value if run.status is defined and run.status and run.status.value is defined else run.status or ("completed" if run.execution_success else "failed") }}  
**Execution Success:** {{ run.execution_success if run.execution_success is not none else "N/A" }}  
**Overall Score:** {{ run.overall_score if run.overall_score is not none else "N/A" }}

### Performance

- Tokens Used: {{ run.tokens_used if run.tokens_used is not none else "N/A" }}
- Generation Latency (ms): {{ run.latency_ms if run.latency_ms is not none else "N/A" }}
- Execution Time (ms): {{ run.execution_time_ms if run.execution_time_ms is not none else "N/A" }}
- Workspace Path: {{ run.workspace_path or "N/A" }}

### Prompt

```text
{{ run.prompt_text or run.prompt or "No prompt captured." }}
```

### Generated Code

```{{ run.language.name if run.language is defined and run.language and run.language.name else language_value|lower if language_value != "N/A" else "python" }}
{{ run.generated_code or run.code or "No generated code captured." }}
```

### Execution Output

**Stdout / Output**

```text
{{ run.execution_output or run.stdout or "No execution output captured." }}
```

**Error Output**

```text
{{ run.execution_error or run.stderr or "No execution errors captured." }}
```

{% if run.correctness is defined and run.correctness %}
### Correctness

- Tested: {{ run.correctness.tested if run.correctness.tested is not none else "N/A" }}
- Passed: {{ run.correctness.passed if run.correctness.passed is not none else "N/A" }}
- Expected: {{ run.correctness.expected if run.correctness.expected is not none else "N/A" }}
- Actual: {{ run.correctness.actual if run.correctness.actual is not none else "N/A" }}
- Reason: {{ run.correctness.reason if run.correctness.reason is not none else "N/A" }}
{% endif %}

{% if run.syntax is defined and run.syntax %}
### Syntax Analysis

- Passed: {{ run.syntax.success if run.syntax.success is not none else "N/A" }}
- Error: {{ run.syntax.error if run.syntax.error else "None" }}
{% endif %}

{% if run.runtime is defined and run.runtime %}
### Runtime Analysis

- Passed: {{ run.runtime.success if run.runtime.success is not none else "N/A" }}
- Execution Time (ms): {{ run.runtime.execution_time_ms if run.runtime.execution_time_ms is not none else "N/A" }}
- Error: {{ run.runtime.error if run.runtime.error else "None" }}
{% endif %}

{% if run.readability is defined and run.readability %}
### Readability

```json
{{ run.readability }}
```
{% endif %}

{% set findings = run.security_findings if run.security_findings is defined and run.security_findings else run.findings if run.findings is defined and run.findings else [] %}
{% if findings %}
### Security Findings

| Severity | Category | Title | File | Line |
| --- | --- | --- | --- | ---: |
{% for finding in findings %}
| {{ finding.severity.value if finding.severity is defined and finding.severity and finding.severity.value is defined else finding.severity or "N/A" }} | {{ finding.category or "N/A" }} | {{ finding.title or "N/A" }} | {{ finding.file_path or "N/A" }} | {{ finding.line_number if finding.line_number is not none else "N/A" }} |
{% endfor %}

{% else %}
### Security Findings

No security findings were recorded for this run.
{% endif %}
{% endfor %}

{% if not run_items %}
## No Results Available

No comparison runs were supplied to this template.
{% endif %}
