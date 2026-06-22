# backend/tests/conftest.py
import pytest
import sys
import os
from datetime import datetime, timedelta
import random

# Add backend to path so imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def make_expense(merchant, amount, category, days_ago=0, is_anomaly=False):
    """Helper: create a single expense dict."""
    return {
        "merchant": merchant,
        "amount": float(amount),
        "category": category,
        "date": datetime.now() - timedelta(days=days_ago),
        "is_anomaly": is_anomaly,
    }


def make_expenses_bulk(n=100, category="Food", avg=500, std=100):
    """Helper: create N realistic expenses with normal distribution."""
    expenses = []
    for i in range(n):
        amount = max(50, random.gauss(avg, std))
        expenses.append(make_expense(
            merchant="Swiggy",
            amount=round(amount, 2),
            category=category,
            days_ago=random.randint(0, 180),
        ))
    return expenses


@pytest.fixture
def normal_food_expenses():
    """100 normal food transactions averaging ₹500."""
    return make_expenses_bulk(100, "Food", avg=500, std=80)


@pytest.fixture
def expenses_with_anomaly(normal_food_expenses):
    """Normal food expenses + 1 obvious anomaly IN THE SAME CATEGORY."""
    # Must be same category (Food) so z-score has a baseline to compare against
    anomaly = make_expense("Expensive Restaurant", 89000, "Food", is_anomaly=True)
    return normal_food_expenses + [anomaly]


@pytest.fixture
def multi_category_expenses():
    """Realistic spread across all categories."""
    expenses = []
    categories = {
        "Food": ("Swiggy", 400, 80),
        "Transport": ("Uber", 200, 50),
        "Shopping": ("Amazon", 2000, 500),
        "Subscription": ("Netflix", 199, 0),
        "Utilities": ("Airtel", 599, 0),
        "Health": ("Apollo Pharmacy", 600, 150),
        "Entertainment": ("PVR Cinemas", 400, 100),
    }
    for category, (merchant, avg, std) in categories.items():
        for i in range(20):
            amount = avg if std == 0 else max(50, random.gauss(avg, std))
            expenses.append(make_expense(
                merchant=merchant,
                amount=round(amount, 2),
                category=category,
                days_ago=random.randint(0, 180),
            ))
    return expenses


@pytest.fixture
def messy_csv_content():
    """CSV with intentional data quality issues."""
    return """date,merchant,amount
2026-01-02,Swiggy,342
2026-01-03,Netflix,199
2026-01-04,Swiggy,342
2026-01-04,Swiggy,342
2026-01-05,,0
2026-01-06,Uber,
2026-01-07,Amazon,1500
2026-01-08,invalid-date,800
"""


@pytest.fixture
def clean_csv_content():
    """Clean generic CSV with no issues."""
    return """date,merchant,amount
2026-01-02,Swiggy,342
2026-01-03,Netflix,199
2026-01-04,Uber,189
2026-01-05,Amazon,1500
2026-01-06,Apollo Pharmacy,680
"""