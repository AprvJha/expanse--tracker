# backend/app/main.py
import sys
# Fix Windows charmap encoding — uvicorn --reload child process
# doesn't inherit PYTHONIOENCODING, causing crashes on Unicode print()
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import db
from ml.ml_categorizer import load_model
from app.api.routes import upload, expenses, auth, categorize, insights, anomaly, prediction, suggestions

app = FastAPI(title="Expense Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await db.command("ping")
    print("[SUCCESS] MongoDB connected")
    load_model()

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(auth.router)         
app.include_router(upload.router)
app.include_router(expenses.router)
app.include_router(categorize.router)
app.include_router(insights.router)
app.include_router(anomaly.router)
app.include_router(prediction.router)
app.include_router(suggestions.router)