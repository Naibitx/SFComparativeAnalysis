from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.tasks import router as t_Router
from app.routes.runs import router as ru_Router
from app.routes.reports import router as re_Router
from app.routes.settings import router as s_Router
from app.db.database import get_db_manager


app = FastAPI(title="AI Comparator Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):[0-9]+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Backend is running"}

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.on_event("startup")
def startup():
    db_manager = get_db_manager()
    db_manager.create_all_tables()

app.include_router(t_Router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(re_Router, prefix="/api/reports", tags=["Reports"])
app.include_router(ru_Router, prefix="/api/evaluations", tags=["Runs"])
app.include_router(s_Router, prefix="/api/admin", tags=["Settings"])