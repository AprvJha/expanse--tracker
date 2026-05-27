# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import db
from ml.ml_categorizer import load_model
from app.api.routes import upload, expenses, auth, categorize, insights, anomaly
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