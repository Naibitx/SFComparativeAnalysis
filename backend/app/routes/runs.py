from fastapi import APIRouter

#below we will import the pipeline logic
from app.services.run_pipeline import r_pipe
router = APIRouter()

@router.post("/")
def run_task(payload: dict):
    '''this here is for the expected input, so forexample task will be = a and assistant would be chatgpt, so you choose which task and which assistant'''

    task_code = payload.get("task_code")
    assistant = payload.get("assistant")

    result = r_pipe(task_code, assistant)#will run the full pipeline

    return result