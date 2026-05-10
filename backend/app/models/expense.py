# backend/app/models/expense.py
from bson import ObjectId
from datetime import datetime


def expense_serializer(expense) -> dict:
    """Convert MongoDB document to JSON-serializable dict."""
    return {
        "id": str(expense["_id"]),
        "user_id": expense.get("user_id", ""),
        "merchant": expense.get("merchant", ""),
        "amount": expense.get("amount", 0.0),
        "category": expense.get("category", "Uncategorized"),
        "date": expense.get("date").isoformat() if expense.get("date") else None,
        "description": expense.get("description", ""),
        "payment_method": expense.get("payment_method", ""),
        "is_anomaly": expense.get("is_anomaly", False),
        "source": expense.get("source", "manual"),
        "created_at": expense.get("created_at").isoformat() if expense.get("created_at") else None,
    }


def expenses_serializer(expenses) -> list:
    return [expense_serializer(e) for e in expenses]