# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import db
from app.core.config import ALLOWED_ORIGINS
from app.api.routes import upload, expenses, auth, categorize, insights, anomaly, prediction, suggestions
from ml.ml_categorizer import load_model
from ml.bootstrap import bootstrap_models

app = FastAPI(title="Expense Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await db.command("ping")
    print("[OK] MongoDB connected")

    await bootstrap_models()
    load_model()

@app.get("/")
def root():
    return {"status": "ok", "message": "Expense Tracker API"}

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