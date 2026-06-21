from ml.ml_categorizer import ml_categorize
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.csv_parser import parse_csv
from app.core.database import get_database
from app.api.routes.auth import get_current_user
from fastapi import Depends
from datetime import datetime

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("/csv")
async def upload_csv(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted")

    content = await file.read()
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        text = content.decode("latin-1")

    try:
        records, stats = parse_csv(text)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    if not records:
        raise HTTPException(
            status_code=422,
            detail="No valid transactions found after cleaning."
        )

    db = get_database()
    user_id = current_user["id"]

    amounts = [float(r["amount"]) for r in records]
    avg_amount = sum(amounts) / len(amounts) if amounts else 0

    documents = []
    for record in records:
        amount = float(record["amount"])
        is_anomaly = amount > (avg_amount * 5) and amount > 1000 
        
        documents.append({
            "user_id": user_id,
            "merchant": record["merchant"],
            "amount": amount,
            "date": record["date"].to_pydatetime() if hasattr(record["date"], "to_pydatetime") else record["date"],
            "category": ml_categorize(record["merchant"])["category"],
            "description": f"{record['merchant']} payment",
            "payment_method": "Unknown",
            "is_anomaly": is_anomaly,
            "source": "csv",
            "created_at": datetime.now(),
        })

    result = await db["expenses"].insert_many(documents)

    return {
        "message": "Upload successful",
        "format_detected": stats["format_detected"],
        "stats": {
            "original_rows": stats["original_rows"],
            "final_rows": stats["final_rows"],
            "dropped_nulls": stats["dropped_nulls"],
            "dropped_duplicates": stats["dropped_duplicates"],
            "dropped_bad_dates": stats["dropped_bad_dates"],
            "dropped_zero_amounts": stats["dropped_zero_amounts"],
        },
        "inserted": len(result.inserted_ids),
    }


@router.get("/preview")
async def preview_csv(file: UploadFile = File(...)):
    """
    Preview first 10 rows WITHOUT saving to DB.
    Used by frontend before user confirms upload.
    """
    content = await file.read()
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        text = content.decode("latin-1")

    try:
        records, stats = parse_csv(text)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    return {
        "format_detected": stats["format_detected"],
        "total_rows": stats["final_rows"],
        "preview": records[:10],  # first 10 rows only
        "stats": stats,
    }