# backend/tests/test_suggestions.py
import pytest
from ml.suggestions.engine import generate_suggestions
from ml.suggestions.rules import (
    check_category_thresholds,
    savings_opportunities,
    subscription_audit,
    diversification_check,
)


def test_suggestions_structure(multi_category_expenses):
    """Every suggestion has required fields."""
    suggestions = generate_suggestions(multi_category_expenses)
    required = ["type", "severity", "title", "message", "recommendation"]
    for s in suggestions:
        for field in required:
            assert field in s, f"Missing field '{field}' in suggestion: {s}"


def test_category_threshold_triggers_on_high_spend():
    """Category over benchmark triggers a suggestion."""
    # Shopping at 80% of total → way over 25% benchmark
    totals = {"Shopping": 8000, "Food": 1000, "Transport": 1000}
    total = sum(totals.values())
    suggestions = check_category_thresholds(totals, total)
    categories_flagged = [s["data"]["category"] for s in suggestions]
    assert "Shopping" in categories_flagged


def test_category_threshold_no_trigger_below_benchmark():
    """Categories genuinely under benchmark do NOT trigger suggestions."""
    # Food at 20% (under 25% benchmark)
    # Transport at 10% (under 15% benchmark)
    # Shopping at 15% (under 25% benchmark)
    totals = {"Food": 2000, "Transport": 1000, "Shopping": 1500}
    total = 10000  # these are 20%, 10%, 15% of a larger total
    suggestions = check_category_thresholds(totals, total)
    assert len(suggestions) == 0


def test_savings_opportunity_calculates_correctly():
    """Savings opportunity math is correct."""
    totals = {"Shopping": 12000}
    total = 12000
    suggestions = savings_opportunities(totals, total, months=1)
    assert len(suggestions) == 1
    s = suggestions[0]
    # 20% of ₹12,000 = ₹2,400
    assert abs(s["data"]["monthly_savings"] - 2400) < 1


def test_subscription_audit_totals_correctly():
    """Subscription audit sums amounts correctly."""
    recurring = [
        {"merchant": "Netflix", "amount": 199, "category": "Subscription"},
        {"merchant": "Spotify", "amount": 119, "category": "Subscription"},
    ]
    result = subscription_audit(recurring)
    assert result is not None
    assert result["data"]["total_monthly"] == 318
    assert result["data"]["total_yearly"] == 318 * 12


def test_subscription_audit_none_on_empty():
    """Empty recurring list returns None."""
    result = subscription_audit([])
    assert result is None


def test_diversification_triggers_above_threshold():
    """Concentration above 60% triggers diversification suggestion."""
    concentration = {
        "top3_percentage": 75.0,
        "top3_categories": ["Shopping", "Food", "Health"],
        "top1_category": "Shopping",
        "top1_percentage": 42.0,
    }
    result = diversification_check(concentration)
    assert result is not None
    assert result["type"] == "diversification"


def test_diversification_no_trigger_below_threshold():
    """Concentration below 60% does NOT trigger suggestion."""
    concentration = {
        "top3_percentage": 55.0,
        "top3_categories": ["Shopping", "Food", "Health"],
        "top1_category": "Shopping",
        "top1_percentage": 25.0,
    }
    result = diversification_check(concentration)
    assert result is None


def test_generate_suggestions_empty_input():
    """Empty expense list returns empty suggestions."""
    suggestions = generate_suggestions([])
    assert suggestions == []


def test_suggestions_sorted_by_severity(multi_category_expenses):
    """High severity suggestions come before medium and info."""
    suggestions = generate_suggestions(multi_category_expenses)
    if len(suggestions) < 2:
        return
    severity_order = {"high": 0, "medium": 1, "low": 2, "info": 3}
    for i in range(len(suggestions) - 1):
        current = severity_order.get(suggestions[i]["severity"], 99)
        next_ = severity_order.get(suggestions[i + 1]["severity"], 99)
        assert current <= next_, "Suggestions not sorted by severity"