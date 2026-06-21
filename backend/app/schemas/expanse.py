from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum

class Category(str, Enum):
    FOOD = "Food"
    TRANSPORT = "Transport"
    SHOPPING = "Shopping"
    SUBSCRIPTION = "Subscription"
    UTILITIES = "Utilities"
    HEALTH = "Health"
    ENTERTAINMENT = "Entertainment"
    OTHER = "Other"

class ExpenseCreate(BaseModel):
    amount: float
    merchant: str
    category: Category
    date: datetime
    description: Optional[str] = None
    payment_method: Optional[str] = None
    is_anomaly: bool = False
    source: str = "manual"

class ExpenseUpdate(BaseModel):
    amount: Optional[float] = None
    merchant: Optional[str] = None
    category: Optional[Category] = None
    date: Optional[datetime] = None
    description: Optional[str] = None
    payment_method: Optional[str] = None
    is_anomaly: Optional[bool] = None
    source: Optional[str] = None

class ExpenseResponse(ExpenseCreate):
    id: str
    user_id: str
    created_at: datetime