import os
from datetime import datetime

from app.services.prompt_builder import build_prompt
from app.services.workspace_manager import create_workspace, save_file
from app.services.execution_engine import run_code
from app.services.metrics_engine import MetricsEngine

engine = MetricsEngine()


def r_pipe(task_code: str, assistant: str, expected_output: str):
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    workspace = create_workspace(run_id, task_code, assistant)

    prompt = build_prompt(task_code)

    generated_code = "print('Holiwis de la IA')"

    code_path = save_file(workspace, "generated_code.py", generated_code)
    save_file(workspace, "prompt.txt", prompt)

    execution = run_code(code_path)

    metrics = engine.evaluate_assistant(
        assistant=assistant,
        prompt=prompt,
        expected_output=expected_output,
        execution=execution
    )

    return {
        "workspace": workspace,
        "execution": execution,
        "metrics": metrics,
    }