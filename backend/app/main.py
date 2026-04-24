from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.tasks import router as t_Router
from app.routes.runs import router as ru_Router
from app.routes.reports import router as re_Router
from app.routes.settings import router as s_Router

app = FastAPI(title="AI Comparator Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def root():
    return {"message": "Testing backend, backend is running YAYY"}

@app.get("/api/health")
def health():
    return {"status": "ok"}

# Register routes with /api prefix
app.include_router(t_Router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(re_Router, prefix="/api/reports", tags=["Reports"])
app.include_router(ru_Router, prefix="/api/evaluations", tags=["Runs"]) 
app.include_router(s_Router, prefix="/api/admin", tags=["Settings"]) 