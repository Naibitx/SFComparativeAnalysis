from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def settings():
    return {
        "message": "Settings module working",
        "framework": "AI assistant evaluation system"
    }