from fastapi import APIRouter

router = APIRouter()
@router.get("/")
def list_tasks():
    #this below will return us all the available tasks
    return [
        {"task_code": "a", "name": "Read text file"},
        {"task_code": "b", "name": "Read JSON with threads"},
        {"task_code": "c", "name": "Write text file"},
        {"task_code": "d", "name": "Write JSON with threads"},
        {"task_code": "e", "name": "Zip file"},
        {"task_code": "f", "name": "MySQL query"},
        {"task_code": "g", "name": "MongoDB query"},
        {"task_code": "h", "name": "Authentication"},
    ]