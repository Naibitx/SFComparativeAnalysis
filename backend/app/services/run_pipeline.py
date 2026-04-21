import os
from datetime import datetime

#below we are imprting our helper modules
from app.services.prompt_builder import build_prompt
from app.services.workspace_manager import create_workspace, save_file
from app.services.execution_engine import run_code
from app.services.metrics_engine import compute_metrics


def r_pipe(task_code: str, assistant: str):

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S") #creating our workspace
    workspace = create_workspace(run_id, task_code, assistant)

    prompt = build_prompt(task_code)#building the prompts

    generated_code = "print('Holiwis de la IA')"#mock code generation

    code_path = save_file(workspace, "generated_code.py", generated_code)#saving our files
    save_file(workspace, "prompt.txt", prompt)

    execution = run_code(code_path)#will execute the code

    metrics = compute_metrics(execution)#compute the metrics we need from the execution 

    return { #the results we would get
        "workspace": workspace,
        "execution": execution,
        "metrics": metrics,
    }