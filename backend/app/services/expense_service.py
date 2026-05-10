# backend/app/services/expense_service.py
from bson import ObjectId
from datetime import datetime
from app.core.database import get_database
from app.models.expense import expense_serializer


db = get_database()
collection = db["expenses"]


async def get_expenses(
    user_id: str,
    page: int = 1,
    limit: int = 50,
    category: str = None,
    start_date: datetime = None,
    end_date: datetime = None,
    source: str = None,
) -> dict:
    """
    Fetch expenses with filters + pagination.
    Returns data + pagination metadata.
    """
    # Build filter query
    query = {"user_id": user_id}

    if category:
        query["category"] = category

    if source:
        query["source"] = source

    if start_date or end_date:
        query["date"] = {}
        if start_date:
            query["date"]["$gte"] = start_date
        if end_date:
            query["date"]["$lte"] = end_date

    # Count total matching documents
    total = await collection.count_documents(query)

    # Fetch paginated results sorted by date descending
    skip = (page - 1) * limit
    cursor = collection.find(query).sort("date", -1).skip(skip).limit(limit)
    expenses = await cursor.to_list(length=limit)

    return {
        "data": [expense_serializer(e) for e in expenses],
        "pagination": {
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit,
        },
    }


async def get_expense_by_id(expense_id: str, user_id: str) -> dict | None:
    """Fetch single expense by ID. Returns None if not found."""
    try:
        expense = await collection.find_one({
            "_id": ObjectId(expense_id),
            "user_id": user_id,
        })
        return expense_serializer(expense) if expense else None
    except Exception:
        return None


async def create_expense(user_id: str, data: dict) -> dict:
    """Insert a new expense document."""
    document = {
        "user_id": user_id,
        "merchant": data["merchant"],
        "amount": float(data["amount"]),
        "category": data.get("category", "Uncategorized"),
        "date": data.get("date", datetime.now()),
        "description": data.get("description", ""),
        "payment_method": data.get("payment_method", ""),
        "is_anomaly": False,
        "source": "manual",
        "created_at": datetime.now(),
    }
    result = await collection.insert_one(document)
    created = await collection.find_one({"_id": result.inserted_id})
    return expense_serializer(created)


async def update_expense(expense_id: str, user_id: str, data: dict) -> dict | None:
    """Update an existing expense. Only updates fields that are provided."""
    # Remove None values so we don't overwrite with null
    updates = {k: v for k, v in data.items() if v is not None}

    if not updates:
        return await get_expense_by_id(expense_id, user_id)

    updates["updated_at"] = datetime.now()

    try:
        result = await collection.update_one(
            {"_id": ObjectId(expense_id), "user_id": user_id},
            {"$set": updates},
        )
        if result.matched_count == 0:
            return None
        return await get_expense_by_id(expense_id, user_id)
    except Exception:
        return None


async def delete_expense(expense_id: str, user_id: str) -> bool:
    """Delete expense. Returns True if deleted, False if not found."""
    try:
        result = await collection.delete_one({
            "_id": ObjectId(expense_id),
            "user_id": user_id,
        })
        return result.deleted_count > 0
    except Exception:
        return False


async def get_summary(user_id: str) -> dict:
    """
    Aggregate summary stats for dashboard.
    Total spend, category breakdown, monthly totals.
    """
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$group": {
            "_id": "$category",
            "total": {"$sum": "$amount"},
            "count": {"$sum": 1},
            "avg": {"$avg": "$amount"},
        }},
        {"$sort": {"total": -1}},
    ]

    category_breakdown = []
    async for doc in collection.aggregate(pipeline):
        category_breakdown.append({
            "category": doc["_id"],
            "total": round(doc["total"], 2),
            "count": doc["count"],
            "avg": round(doc["avg"], 2),
        })

    # Total across all categories
    total_spent = sum(c["total"] for c in category_breakdown)
    total_transactions = sum(c["count"] for c in category_breakdown)

    # Monthly breakdown (last 6 months)
    monthly_pipeline = [
        {"$match": {"user_id": user_id}},
        {"$group": {
            "_id": {
                "year": {"$year": "$date"},
                "month": {"$month": "$date"},
            },
            "total": {"$sum": "$amount"},
            "count": {"$sum": 1},
        }},
        {"$sort": {"_id.year": 1, "_id.month": 1}},
        {"$limit": 6},
    ]

    monthly_breakdown = []
    async for doc in collection.aggregate(monthly_pipeline):
        monthly_breakdown.append({
            "year": doc["_id"]["year"],
            "month": doc["_id"]["month"],
            "total": round(doc["total"], 2),
            "count": doc["count"],
        })

    return {
        "total_spent": round(total_spent, 2),
        "total_transactions": total_transactions,
        "category_breakdown": category_breakdown,
        "monthly_breakdown": monthly_breakdown,
    }