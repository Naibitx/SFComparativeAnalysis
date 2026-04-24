from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_reports():
    return {
        "message": "Reports module working",
        "available_tasks": ["a", "b", "c", "d", "e", "f", "g", "h"]
    }

