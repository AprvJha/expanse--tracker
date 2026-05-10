# backend/app/api/routes/categorize.py
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from ml.ml_categorizer import ml_categorize, bulk_ml_categorize, get_model_metrics
from ml.categorizer import keyword_categorize
from app.api.routes.auth import get_current_user
from app.core.database import get_database
from bson import ObjectId

router = APIRouter(prefix="/categorize", tags=["categorize"])


class CategorizeRequest(BaseModel):
    merchant: str


class BulkCategorizeRequest(BaseModel):
    merchants: list[str]


class CorrectCategoryRequest(BaseModel):
    expense_id: str
    correct_category: str


@router.post("/single")
async def categorize_single(
    data: CategorizeRequest,
    current_user: dict = Depends(get_current_user),
):
    """Categorize a single merchant using ML model."""
    ml_result = ml_categorize(data.merchant)
    keyword_result, _ = keyword_categorize(data.merchant)

    return {
        "merchant": data.merchant,
        "ml_prediction": ml_result,
        "keyword_prediction": keyword_result,
    }


@router.post("/bulk")
async def categorize_bulk(
    data: BulkCategorizeRequest,
    current_user: dict = Depends(get_current_user),
):
    """Categorize multiple merchants at once."""
    results = bulk_ml_categorize(data.merchants)
    return {"results": results, "count": len(results)}


@router.post("/correct")
async def correct_category(
    data: CorrectCategoryRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    User corrects a wrong category.
    Saves correction to DB — used for model retraining later.
    """
    db = get_database()

    await db["expenses"].update_one(
        {"_id": ObjectId(data.expense_id), "user_id": current_user["id"]},
        {"$set": {
            "category": data.correct_category,
            "user_corrected": True,
        }}
    )

    return {"message": "Category updated", "new_category": data.correct_category}


@router.get("/metrics")
async def model_metrics(current_user: dict = Depends(get_current_user)):
    """
    Return model performance metrics.
    Baseline accuracy vs ML accuracy — shown on dashboard.
    """
    return get_model_metrics()