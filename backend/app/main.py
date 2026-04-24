from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware #this to connect frontedn and backend
#below we have our router imports 
from app.routes.tasks import router as t_Router
from app.routes.runs import router as ru_Router
from app.routes.reports import router as re_Router
from app.routes.settings import router as s_Router

app= FastAPI(title= "AI Comparator Assistant")
app.add_middleware(
    CORSMiddleware,
    allow_origins= ["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers= ["*"]
)

@app.get("/")
def root():
    return{"message": "Tesitng backend, backend is running YAYY"}

#below we are registering the routes
app.include_router(t_Router, prefix="/tasks", tags=["Tasks"])
app.include_router(re_Router, prefix="/reports", tags=["Reports"])
app.include_router(ru_Router, prefix="/runs", tags=["Runs"])
app.include_router(s_Router, prefix="/settings", tags=["Settings"])
